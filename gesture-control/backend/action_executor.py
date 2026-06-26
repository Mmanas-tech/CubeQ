"""
System action execution for AirDesk gestures.

Maps gesture labels to configured action names (via gesture-control backend config)
and executes the corresponding OS interaction using:
- pyautogui for mouse movement/clicking and keyboard shortcuts
- keyboard for key presses
- mouse for scrolling and mouse interactions where appropriate

All actions are:
- wrapped in try/except (never crash server)
- guarded by a cooldown system (same action cannot trigger within ACTION_COOLDOWN_MS)
- exposed via execute(gesture_label) as the single entry point
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Dict, Optional, Tuple

import keyboard as kb
import mouse as mouse_lib
import pyautogui

from gesture_control.backend.config import ACTION_COOLDOWN_MS, GESTURE_ACTION_MAP

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Execute gesture-mapped system actions with cooldown."""

    def __init__(self, gesture_action_map: Optional[Dict[str, str]] = None) -> None:
        """Initialize executor.

        Args:
            gesture_action_map: mapping from gesture_label -> action_name

        Returns:
            None
        """
        self._gesture_action_map: Dict[str, str] = dict(gesture_action_map or GESTURE_ACTION_MAP)
        self._last_action_time_ms: Dict[str, float] = {}
        self._lock = threading.Lock()

        # Make pyautogui safer in automation environments
        try:
            pyautogui.FAILSAFE = True
        except Exception:
            logger.debug("pyautogui FAILSAFE not set", exc_info=True)

    def _cooldown_allows(self, action_name: str) -> bool:
        """Check whether action cooldown allows execution.

        Args:
            action_name: action to check

        Returns:
            bool: True if allowed, False otherwise
        """
        now_ms = time.time() * 1000.0
        with self._lock:
            last = self._last_action_time_ms.get(action_name)
            if last is not None and (now_ms - last) < float(ACTION_COOLDOWN_MS):
                return False
            self._last_action_time_ms[action_name] = now_ms
            return True

    def execute(self, gesture_label: str) -> str:
        """Execute system action for the given gesture label.

        Args:
            gesture_label: predicted gesture label (e.g., "thumbs_up")

        Returns:
            str: action_triggered (action_name) actually executed, or "no_action"
        """
        action_name = self._gesture_action_map.get(gesture_label, "no_action")

        if action_name == "no_action":
            return "no_action"

        if not self._cooldown_allows(action_name):
            return f"{action_name}_cooldown"

        try:
            self._execute_action(action_name)
            return action_name
        except Exception:
            logger.exception("Failed executing action=%s for gesture=%s", action_name, gesture_label)
            return "no_action"

    def _execute_action(self, action_name: str) -> None:
        """Dispatch actual action execution.

        Args:
            action_name: action name to execute

        Returns:
            None
        """
        step = 50

        if action_name == "move_mouse_up":
            pyautogui.moveRel(0, -step, duration=0.0)
        elif action_name == "move_mouse_down":
            pyautogui.moveRel(0, step, duration=0.0)
        elif action_name == "move_mouse_left":
            pyautogui.moveRel(-step, 0, duration=0.0)
        elif action_name == "move_mouse_right":
            pyautogui.moveRel(step, 0, duration=0.0)

        elif action_name == "left_click":
            pyautogui.click(button="left")
        elif action_name == "right_click":
            pyautogui.click(button="right")
        elif action_name == "double_click":
            pyautogui.doubleClick()

        elif action_name == "scroll_up":
            pyautogui.scroll(100)
        elif action_name == "scroll_down":
            pyautogui.scroll(-100)

        elif action_name == "volume_up":
            kb.send("volume up")
        elif action_name == "volume_down":
            kb.send("volume down")
        elif action_name == "mute":
            kb.send("mute")

        elif action_name == "screenshot":
            # Windows: Win+Shift+S opens Snip & Sketch (user choice). Non-modal best effort.
            pyautogui.hotkey("win", "shift", "s")

        elif action_name == "copy":
            pyautogui.hotkey("ctrl", "c")
        elif action_name == "paste":
            pyautogui.hotkey("ctrl", "v")
        elif action_name == "undo":
            pyautogui.hotkey("ctrl", "z")

        elif action_name == "next_tab":
            pyautogui.hotkey("ctrl", "tab")
        elif action_name == "prev_tab":
            pyautogui.hotkey("ctrl", "shift", "tab")
        elif action_name == "close_tab":
            pyautogui.hotkey("ctrl", "w")

        elif action_name == "play_pause":
            pyautogui.hotkey("space")

        elif action_name == "minimize_window":
            pyautogui.hotkey("win", "down")
        elif action_name == "maximize_window":
            pyautogui.hotkey("win", "up")

        else:
            logger.warning("Unknown action_name=%s; ignoring", action_name)
            return
