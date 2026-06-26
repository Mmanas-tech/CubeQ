"""
Feature extraction from hand landmarks.

Takes hand_tracker output (21 landmarks with x/y/z) and produces:
- raw feature vector of size 63 (x,y,z for each landmark)
- normalized feature vector by translating wrist (landmark 0) to origin and scaling
  by max distance from wrist

Optionally angle-based features between finger joints can be included; for now
we keep vector size fixed to 63 per requirement.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Sequence, Tuple

import numpy as np

from gesture_control.backend.config import FEATURE_VECTOR_SIZE

logger = logging.getLogger(__name__)


def get_feature_names() -> List[str]:
    """Return names for each feature in the flattened vector.

    Args:
        None

    Returns:
        List[str]: feature names in the same order as the feature vector
    """
    # 21 landmarks * (x,y,z)
    names: List[str] = []
    for i in range(21):
        names.append(f"lm{i}_x")
        names.append(f"lm{i}_y")
        names.append(f"lm{i}_z")
    return names


def _extract_xyz(landmarks: Sequence[Dict[str, float]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract x/y/z arrays from landmark dicts.

    Args:
        landmarks: sequence of 21 dicts with keys x,y,z

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: x, y, z arrays each shape (21,)
    """
    xs = np.array([float(lm.get("x", 0.0)) for lm in landmarks], dtype=np.float32)
    ys = np.array([float(lm.get("y", 0.0)) for lm in landmarks], dtype=np.float32)
    zs = np.array([float(lm.get("z", 0.0)) for lm in landmarks], dtype=np.float32)
    return xs, ys, zs


def extract_features(
    landmarks_21: Sequence[Dict[str, float]],
    normalize: bool = True,
) -> np.ndarray:
    """Compute a 63-d feature vector from 21 hand landmarks.

    Args:
        landmarks_21: list/sequence of 21 dicts with keys x, y, z (normalized by MediaPipe)
        normalize: if True, translate wrist to origin and scale by max distance from wrist

    Returns:
        np.ndarray: flat numpy array of shape (63,)
    """
    if len(landmarks_21) != 21:
        logger.warning("Expected 21 landmarks, got %s", len(landmarks_21))
        # Best-effort: pad/truncate to 21
        lm = list(landmarks_21)[:21]
        while len(lm) < 21:
            lm.append({"x": 0.0, "y": 0.0, "z": 0.0})
        landmarks_21 = lm

    xs, ys, zs = _extract_xyz(landmarks_21)

    if not normalize:
        feat = np.stack([xs, ys, zs], axis=1).reshape(-1)
        if feat.shape[0] != FEATURE_VECTOR_SIZE:
            feat = np.resize(feat, (FEATURE_VECTOR_SIZE,))
        return feat.astype(np.float32)

    # Normalize: translate by wrist (landmark 0)
    wrist = np.array([xs[0], ys[0], zs[0]], dtype=np.float32)
    pts = np.stack([xs, ys, zs], axis=1).astype(np.float32)  # (21,3)
    pts = pts - wrist[None, :]

    # Scale by max distance from wrist in XYZ
    dists = np.linalg.norm(pts, axis=1)  # (21,)
    max_dist = float(np.max(dists)) if dists.size else 0.0
    if max_dist < 1e-8:
        max_dist = 1.0

    pts = pts / max_dist

    feat = pts.reshape(-1)
    if feat.shape[0] != FEATURE_VECTOR_SIZE:
        feat = np.resize(feat, (FEATURE_VECTOR_SIZE,))
    return feat.astype(np.float32)
