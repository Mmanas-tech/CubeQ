"""
Model loading and prediction management for AirDesk.

Supports four model types:
- random_forest: scikit-learn classifier saved with joblib (.pkl)
- xgboost: XGBoost classifier saved with joblib (.pkl)
- mlp: PyTorch model saved with torch.save state or full module (.pt)
- lstm: PyTorch model saved with torch.save state or full module (.pt)

Provides:
- hot-swappable model loading at runtime without restarting server
- predict(feature_vector) -> (gesture_label, confidence)
- get_loaded_model_info() describing model type/classes/input size

This module is designed to fail gracefully and never crash callers.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import joblib
import numpy as np
import torch

from gesture_control.backend.config import SUPPORTED_MODEL_TYPES

logger = logging.getLogger(__name__)


@dataclass
class LoadedModelInfo:
    """Describes the loaded model for status endpoint/logging."""

    model_type: str
    classes: List[str]
    input_size: int


class ModelManager:
    """Loads/switches models and provides prediction."""

    def __init__(self, default_model_type: str = "random_forest", default_model_path: str = "") -> None:
        """Initialize model manager.

        Args:
            default_model_type: one of SUPPORTED_MODEL_TYPES
            default_model_path: base path where models are stored (optional)

        Returns:
            None
        """
        self._model_type: Optional[str] = None
        self._model: Any = None
        self._classes: List[str] = []
        self._input_size: int = 0

        self._default_model_type = default_model_type
        self._default_model_path = default_model_path

    def _resolve_model_path(self, model_type: str, model_path: str) -> str:
        """Resolve an actual model file path.

        Args:
            model_type: model type key
            model_path: provided path or base directory

        Returns:
            str: resolved path to a file
        """
        if os.path.isfile(model_path):
            return model_path

        # Best-effort: treat as directory and look for expected filename patterns.
        # If config filenames are used elsewhere, callers can pass full paths.
        candidate = os.path.join(model_path, f"{model_type}.pkl" if model_type in {"random_forest", "xgboost"} else f"{model_type}.pt")
        return candidate

    def load_model(self, model_type: str, model_path: str) -> None:
        """Hot-swap to a new model.

        Args:
            model_type: one of SUPPORTED_MODEL_TYPES
            model_path: model file path or base directory

        Returns:
            None
        """
        if model_type not in SUPPORTED_MODEL_TYPES:
            raise ValueError(f"Unsupported model type: {model_type}")

        resolved = self._resolve_model_path(model_type, model_path)
        if not os.path.exists(resolved):
            raise FileNotFoundError(f"Model not found at: {resolved}")

        try:
            if model_type in {"random_forest", "xgboost"}:
                self._load_sklearn_like(model_type, resolved)
            elif model_type in {"mlp", "lstm"}:
                self._load_pytorch(model_type, resolved)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

            self._model_type = model_type
            logger.info("Model loaded successfully: type=%s path=%s", model_type, resolved)
        except Exception:
            logger.exception("Failed to load model: type=%s path=%s", model_type, model_path)
            # Reset state so server can continue safe no-action behavior.
            self._model = None
            self._model_type = None
            self._classes = []
            self._input_size = 0
            raise

    def _load_sklearn_like(self, model_type: str, path: str) -> None:
        """Load sklearn/XGBoost model saved with joblib.

        Args:
            model_type: model type string
            path: full model file path

        Returns:
            None
        """
        model = joblib.load(path)

        # Determine classes
        classes: List[str] = []
        input_size = 0

        # scikit-learn estimators expose classes_
        if hasattr(model, "classes_"):
            try:
                classes = [str(c) for c in list(model.classes_)]
            except Exception:
                classes = []

        # input size is not standard; fall back to 63 (feature vector size) when unknown.
        if hasattr(model, "n_features_in_"):
            try:
                input_size = int(model.n_features_in_)
            except Exception:
                input_size = 0

        if not classes:
            # Best-effort fallback (unknown classes)
            logger.warning("Model classes not found in estimator; using numeric indices.")
            # We keep classes empty; prediction will still work if predict_proba returns correct ordering.
        if input_size <= 0:
            input_size = 63

        self._model = model
        self._classes = classes
        self._input_size = input_size

    def _load_pytorch(self, model_type: str, path: str) -> None:
        """Load a PyTorch model.

        The exported model may be either:
        - a full torch.nn.Module
        - a state_dict + saved metadata JSON next to it (best-effort)

        Args:
            model_type: model type string
            path: full model file path

        Returns:
            None
        """
        loaded = torch.load(path, map_location="cpu")

        # If torch.load returns a tuple/dict with metadata, attempt to parse it.
        # We support common export formats:
        # - {"state_dict": ..., "classes": [...], "input_size": 63}
        # - state_dict directly with companion metadata json at same base name.
        model_obj: Any = None
        classes: List[str] = []
        input_size: int = 63

        if isinstance(loaded, dict) and "state_dict" in loaded:
            state_dict = loaded["state_dict"]
            classes = [str(c) for c in loaded.get("classes", [])] if loaded.get("classes") else []
            input_size = int(loaded.get("input_size", 63))

            # A full architecture is not specified in requirements; we can't safely reconstruct.
            # Therefore, we expect the exported file to contain full module weights OR already-constructed module.
            # If export did torch.save(model.state_dict()), we cannot rebuild without architecture.
            raise RuntimeError(
                "PyTorch checkpoint appears to be state_dict-only. Export full model module or include architecture metadata."
            )

        if isinstance(loaded, torch.nn.Module):
            model_obj = loaded
            classes = [str(c) for c in getattr(model_obj, "classes", [])] if hasattr(model_obj, "classes") else []
        elif isinstance(loaded, dict):
            # If dict-like but without state_dict key, treat as state dict only.
            if all(isinstance(k, str) for k in loaded.keys()):
                # cannot reconstruct architecture
                raise RuntimeError(
                    "PyTorch checkpoint loaded as state-dict-only; export full model or adjust export_model to include module."
                )
        else:
            raise RuntimeError("Unrecognized PyTorch checkpoint format.")

        if model_obj is None:
            raise RuntimeError("Failed to build PyTorch model object from checkpoint.")

        model_obj.eval()
        self._model = model_obj
        self._classes = classes
        self._input_size = input_size

    def predict(self, feature_vector: np.ndarray) -> Tuple[str, float]:
        """Predict gesture for a single feature vector.

        Args:
            feature_vector: numpy array of shape (FEATURE_VECTOR_SIZE,)

        Returns:
            Tuple[str, float]: (gesture_label, confidence)
        """
        if self._model is None or self._model_type is None:
            return ("no_hand", 0.0)

        try:
            x = np.asarray(feature_vector, dtype=np.float32)
            if x.ndim != 1:
                x = x.reshape(-1)

            # Basic input size check
            if self._input_size > 0 and x.shape[0] != self._input_size:
                # Resize best-effort; avoids crash
                x = np.resize(x, (self._input_size,))

            if self._model_type in {"random_forest", "xgboost"}:
                # sklearn-like
                if hasattr(self._model, "predict_proba"):
                    probs = self._model.predict_proba(x.reshape(1, -1))[0]
                    pred_idx = int(np.argmax(probs))
                    confidence = float(probs[pred_idx])
                    gesture_label = (
                        self._classes[pred_idx] if self._classes and pred_idx < len(self._classes) else str(pred_idx)
                    )
                    return gesture_label, confidence

                # fallback
                pred = self._model.predict(x.reshape(1, -1))[0]
                return str(pred), 0.0

            # PyTorch
            if self._model_type in {"mlp", "lstm"}:
                with torch.no_grad():
                    tensor = torch.from_numpy(x).float().unsqueeze(0)  # (1, features)
                    logits = self._model(tensor)
                    probs_t = torch.softmax(logits, dim=-1)[0]
                    pred_idx = int(torch.argmax(probs_t).item())
                    confidence = float(probs_t[pred_idx].item())
                    gesture_label = (
                        self._classes[pred_idx] if self._classes and pred_idx < len(self._classes) else str(pred_idx)
                    )
                    return gesture_label, confidence

            return ("no_hand", 0.0)
        except Exception:
            logger.exception("Prediction failed")
            return ("no_hand", 0.0)

    def get_loaded_model_info(self) -> Dict[str, Any]:
        """Return information about the loaded model.

        Args:
            None

        Returns:
            Dict[str, Any]: model info payload
        """
        if self._model is None or self._model_type is None:
            return {"loaded": False, "model_type": None, "classes": [], "input_size": 0}

        return {
            "loaded": True,
            "model_type": self._model_type,
            "classes": list(self._classes),
            "input_size": self._input_size,
        }
