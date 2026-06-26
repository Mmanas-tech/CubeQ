"""
AirDesk Gesture Control backend configuration.

Centralizes all constants, model/action mappings, database settings, and
websocket/processing parameters used across the backend.
"""

from __future__ import annotations

from typing import Dict, List


# -----------------------------
# WebSocket / FastAPI settings
# -----------------------------
WS_HOST: str = "0.0.0.0"
WS_PORT: int = 8000

# Confidence threshold for triggering a gesture/action
CONFIDENCE_THRESHOLD: float = 0.75

# Process every Nth received frame (server-side skip rate)
FRAME_SKIP_RATE: int = 2

# Landmark configuration
LANDMARK_COUNT: int = 21
FEATURE_VECTOR_SIZE: int = 63  # 21 landmarks * (x,y,z)

# Gesture smoothing
SMOOTHING_BUFFER_SIZE: int = 5
STABLE_GESTURE_MIN_COUNT: int = 3  # same gesture 3/5 times

# Action cooldown (milliseconds)
ACTION_COOLDOWN_MS: int = 500

# -----------------------------
# Models
# -----------------------------
SUPPORTED_MODEL_TYPES: List[str] = ["random_forest", "xgboost", "mlp", "lstm"]

# Default model path (may be replaced at runtime via set_model control message)
DEFAULT_MODEL_PATH: str = "gesture-control/models/"

# Expected filename patterns (best-effort defaults; actual hot-swap uses paths discovered/constructed)
DEFAULT_MODEL_FILENAME: Dict[str, str] = {
    "random_forest": "random_forest.pkl",
    "xgboost": "xgboost.pkl",
    "mlp": "mlp.pt",
    "lstm": "lstm.pt",
}

# When loading a model, attempts these extensions per type
MODEL_EXTENSIONS: Dict[str, List[str]] = {
    "random_forest": [".pkl"],
    "xgboost": [".pkl"],
    "mlp": [".pt"],
    "lstm": [".pt"],
}

# -----------------------------
# Gesture -> Action mapping
# -----------------------------
GESTURE_ACTION_MAP: Dict[str, str] = {
    "thumbs_up": "volume_up",
    "thumbs_down": "volume_down",
    "peace": "screenshot",
    "open_palm": "scroll_up",
    "fist": "scroll_down",
    "point_up": "move_mouse_up",
    "point_down": "move_mouse_down",
    "point_left": "move_mouse_left",
    "point_right": "move_mouse_right",
    "ok": "left_click",
    "call": "play_pause",
    "rock": "mute",
    "pinch": "right_click",
    "two_fingers": "double_click",
    "three_fingers": "next_tab",
    "four_fingers": "prev_tab",
    "no_hand": "no_action",
}

# -----------------------------
# Database
# -----------------------------
DB_PATH: str = "gesture-control/backend/airdesk.db"

# -----------------------------
# MediaPipe / tracker settings
# -----------------------------
MEDIAPIPE_MAX_NUM_HANDS: int = 2
MIN_DETECTION_CONFIDENCE: float = 0.7
MIN_TRACKING_CONFIDENCE: float = 0.5

# -----------------------------
# Misc / protocol
# -----------------------------
SERVER_VERSION: str = "1.0"
