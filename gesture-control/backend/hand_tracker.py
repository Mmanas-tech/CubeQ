"""
Hand landmark extraction using MediaPipe Hands.

Converts OpenCV BGR frames to RGB, runs MediaPipe Hands detection, and returns:
- list of hands detected (0..max_num_hands)
- for each hand: landmarks (21 points with normalized x/y/z), handedness, and bbox
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import cv2
import mediapipe as mp
import numpy as np

from gesture_control.backend.config import (
    MEDIAPIPE_MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
)

logger = logging.getLogger(__name__)


class HandTracker:
    """MediaPipe-backed hand tracker."""

    def __init__(self) -> None:
        """Initialize MediaPipe Hands detector."""
        try:
            self._mp_hands = mp.solutions.hands
            self._hands = self._mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=MEDIAPIPE_MAX_NUM_HANDS,
                min_detection_confidence=MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
            )
        except Exception:
            logger.exception("Failed to initialize MediaPipe Hands")
            # Fail-safe: create no detector; downstream returns empty lists.

            self._hands = None

    def track(self, frame_bgr: np.ndarray) -> List[Dict[str, Any]]:
        """Detect hands and extract landmarks.

        Args:
            frame_bgr: OpenCV frame in BGR format as a numpy array.

        Returns:
            List of hands; each element:
            {
              "landmarks": [{"x": float,"y": float,"z": float}, ... 21 items],
              "handedness": "Left"|"Right",
              "bbox": [x_min,y_min,x_max,y_max] in pixel coordinates
            }
        """
        if frame_bgr is None:
            return []

        if self._hands is None:
            return []

        try:
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            height, width = frame_bgr.shape[:2]

            results = self._hands.process(frame_rgb)
            if not results.multi_hand_landmarks:
                return []

            hands_out: List[Dict[str, Any]] = []
            multi_handedness = results.multi_handedness or []

            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Landmarks are normalized in MediaPipe: x,y in [0,1], z in ~[-1,1] (relative)
                landmarks: List[Dict[str, float]] = []
                xs: List[float] = []
                ys: List[float] = []
                zs: List[float] = []

                for lm in hand_landmarks.landmark:
                    xs.append(float(lm.x))
                    ys.append(float(lm.y))
                    zs.append(float(lm.z))

                    landmarks.append({"x": float(lm.x), "y": float(lm.y), "z": float(lm.z)})

                x_min = int(max(0.0, min(xs)) * width)
                y_min = int(max(0.0, min(ys)) * height)
                x_max = int(min(1.0, max(xs)) * width)
                y_max = int(min(1.0, max(ys)) * height)

                handedness_label = "Unknown"
                try:
                    if idx < len(multi_handedness) and multi_handedness[idx] is not None:
                        handedness_label = multi_handedness[idx].classification[0].label  # type: ignore[index]
                except Exception:
                    logger.debug("Failed to read handedness; defaulting to Unknown", exc_info=True)

                hands_out.append(
                    {
                        "landmarks": landmarks,
                        "handedness": handedness_label,
                        "bbox": [x_min, y_min, x_max, y_max],
                    }
                )

            return hands_out
        except Exception:
            logger.exception("Hand tracking failed")
            return []
