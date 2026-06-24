from typing import Dict, List, Tuple, Optional
from core.cube import ALL_FACES, COLORS, SOLVED_STATE, FACE_U, FACE_D, FACE_F, FACE_B, FACE_L, FACE_R


def validate_cube(state: Dict[str, List[str]]) -> Tuple[bool, Optional[str]]:
    if not isinstance(state, dict):
        return False, "State must be a dictionary"
    for face in ALL_FACES:
        if face not in state:
            return False, f"Missing face: {face}"
        if len(state[face]) != 9:
            return False, f"Face {face} must have 9 stickers, got {len(state[face])}"
        for i, s in enumerate(state[face]):
            if s not in COLORS:
                return False, f"Invalid color '{s}' at {face}[{i}]"
    color_counts = {}
    for face in ALL_FACES:
        for s in state[face]:
            color_counts[s] = color_counts.get(s, 0) + 1
    for color in COLORS:
        if color_counts.get(color, 0) != 9:
            return False, f"Color {color} appears {color_counts.get(color, 0)} times, expected 9"
    center_colors = [state[face][4] for face in ALL_FACES]
    if len(set(center_colors)) != 6:
        return False, "Center stickers must all be different colors"
    return True, None


def is_reachable(state: Dict[str, List[str]]) -> Tuple[bool, Optional[str]]:
    valid, err = validate_cube(state)
    if not valid:
        return False, err
    return True, None
