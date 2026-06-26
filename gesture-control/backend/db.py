"""
SQLite database utilities for AirDesk gesture control.

Provides:
- init_db(): create tables and seed default gesture_configs
- log_gesture(): insert gesture prediction logs
- get_recent_gestures(): recent logs
- update_gesture_action(): update mapping in gesture_configs
- get_all_configs(): list all configs
- get_session_stats(): compute stats for current session
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from gesture_control.backend.config import DB_PATH, GESTURE_ACTION_MAP

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SessionStats:
    """Session statistics returned by get_session_stats()."""

    session_start: float
    total_gestures: int
    unique_gestures_used: int


def _get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with sensible defaults.

    Args:
        None

    Returns:
        sqlite3.Connection: active connection
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the SQLite database: create tables and seed gesture configs.

    Args:
        None

    Returns:
        None
    """
    try:
        with _get_connection() as conn:
            cur = conn.cursor()

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS gesture_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    gesture_label TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    hand TEXT NOT NULL,
                    action_triggered TEXT NOT NULL,
                    processing_time_ms REAL NOT NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS gesture_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gesture_label TEXT NOT NULL UNIQUE,
                    action_name TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS session_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_start REAL NOT NULL,
                    session_end REAL
                )
                """
            )

            # Seed default configs if table empty
            cur.execute("SELECT COUNT(*) AS c FROM gesture_configs")
            row = cur.fetchone()
            count = int(row["c"]) if row else 0

            if count == 0:
                now = time.time()
                for gesture_label, action_name in GESTURE_ACTION_MAP.items():
                    cur.execute(
                        """
                        INSERT INTO gesture_configs (gesture_label, action_name, enabled, created_at, updated_at)
                        VALUES (?, ?, 1, ?, ?)
                        """,
                        (gesture_label, action_name, now, now),
                    )

            # Ensure there is an open session row
            cur.execute("SELECT id, session_start FROM session_stats WHERE session_end IS NULL ORDER BY id DESC LIMIT 1")
            existing = cur.fetchone()
            if existing is None:
                cur.execute("INSERT INTO session_stats (session_start, session_end) VALUES (?, NULL)", (time.time(),))

            conn.commit()
    except Exception:
        logger.exception("Failed to initialize DB")


def log_gesture(
    gesture_label: str,
    confidence: float,
    hand: str,
    action_triggered: str,
    processing_time_ms: float,
) -> None:
    """Insert a gesture prediction log row.

    Args:
        gesture_label: predicted gesture label
        confidence: prediction confidence
        hand: handedness ("Left"/"Right"/etc.)
        action_triggered: executed action name
        processing_time_ms: end-to-end processing time in ms

    Returns:
        None
    """
    try:
        with _get_connection() as conn:
            conn.execute(
                """
                INSERT INTO gesture_logs (timestamp, gesture_label, confidence, hand, action_triggered, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (time.time(), gesture_label, float(confidence), str(hand), str(action_triggered), float(processing_time_ms)),
            )
            conn.commit()
    except Exception:
        logger.exception("Failed to log gesture")


def get_recent_gestures(limit: int = 50) -> List[Dict[str, Any]]:
    """Return last N gesture logs.

    Args:
        limit: max number of rows to return

    Returns:
        List[Dict[str, Any]]: log rows
    """
    try:
        lim = max(1, int(limit))
        with _get_connection() as conn:
            cur = conn.execute(
                """
                SELECT id, timestamp, gesture_label, confidence, hand, action_triggered, processing_time_ms
                FROM gesture_logs
                ORDER BY id DESC
                LIMIT ?
                """,
                (lim,),
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    except Exception:
        logger.exception("Failed to fetch recent gestures")
        return []


def update_gesture_action(gesture_label: str, action_name: str) -> bool:
    """Update gesture action mapping in gesture_configs.

    Args:
        gesture_label: gesture label key
        action_name: new action name

    Returns:
        bool: True if updated, False otherwise
    """
    try:
        with _get_connection() as conn:
            now = time.time()
            cur = conn.execute(
                """
                UPDATE gesture_configs
                SET action_name = ?, updated_at = ?
                WHERE gesture_label = ?
                """,
                (action_name, now, gesture_label),
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception:
        logger.exception("Failed to update gesture action mapping")
        return False


def get_all_configs() -> List[Dict[str, Any]]:
    """Fetch all gesture configs.

    Args:
        None

    Returns:
        List[Dict[str, Any]]: list of gesture configs
    """
    try:
        with _get_connection() as conn:
            cur = conn.execute(
                """
                SELECT gesture_label, action_name, enabled, created_at, updated_at
                FROM gesture_configs
                ORDER BY gesture_label ASC
                """
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    except Exception:
        logger.exception("Failed to fetch all configs")
        return []


def get_session_stats() -> Dict[str, Any]:
    """Compute and return session statistics for current session.

    Stats:
    - session_start: session start timestamp
    - total_gestures: number of gesture_logs rows in the session duration
    - unique_gestures_used: count distinct gesture_label values in session

    Args:
        None

    Returns:
        Dict[str, Any]: stats payload
    """
    try:
        with _get_connection() as conn:
            cur = conn.execute(
                "SELECT session_start FROM session_stats WHERE session_end IS NULL ORDER BY id DESC LIMIT 1"
            )
            row = cur.fetchone()
            session_start = float(row["session_start"]) if row else time.time()

            cur2 = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_gestures,
                    COUNT(DISTINCT gesture_label) AS unique_gestures_used
                FROM gesture_logs
                WHERE timestamp >= ?
                """,
                (session_start,),
            )
            row2 = cur2.fetchone()
            total = int(row2["total_gestures"]) if row2 else 0
            unique_used = int(row2["unique_gestures_used"]) if row2 else 0

            return {
                "session_start": session_start,
                "session_end": None,
                "total_gestures": total,
                "unique_gestures_used": unique_used,
            }
    except Exception:
        logger.exception("Failed to compute session stats")
        return {
            "session_start": time.time(),
            "session_end": None,
            "total_gestures": 0,
            "unique_gestures_used": 0,
        }


def end_current_session() -> None:
    """Mark the current session as ended (session_end timestamp).

    Args:
        None

    Returns:
        None
    """
    try:
        with _get_connection() as conn:
            conn.execute(
                "UPDATE session_stats SET session_end = ? WHERE session_end IS NULL",
                (time.time(),),
            )
            conn.commit()
    except Exception:
        logger.exception("Failed to end current session")
