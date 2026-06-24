from typing import Dict, List
from core.cube import (
    ALL_FACES, FACE_U, FACE_D, FACE_F, FACE_B, FACE_L, FACE_R,
    SOLVED_STATE, state_to_tuple
)

EDGES = [
    ((FACE_U, 7), (FACE_F, 1)),
    ((FACE_U, 5), (FACE_R, 1)),
    ((FACE_U, 1), (FACE_B, 1)),
    ((FACE_U, 3), (FACE_L, 1)),
    ((FACE_D, 7), (FACE_F, 7)),
    ((FACE_D, 5), (FACE_R, 7)),
    ((FACE_D, 1), (FACE_B, 7)),
    ((FACE_D, 3), (FACE_L, 7)),
    ((FACE_F, 5), (FACE_R, 3)),
    ((FACE_F, 3), (FACE_L, 5)),
    ((FACE_B, 3), (FACE_R, 5)),
    ((FACE_B, 5), (FACE_L, 3)),
]

CORNERS = [
    ((FACE_U, 8), (FACE_F, 2), (FACE_R, 0)),
    ((FACE_U, 6), (FACE_F, 0), (FACE_L, 2)),
    ((FACE_U, 2), (FACE_B, 2), (FACE_R, 2)),
    ((FACE_U, 0), (FACE_B, 0), (FACE_L, 0)),
    ((FACE_D, 2), (FACE_F, 6), (FACE_R, 8)),
    ((FACE_D, 0), (FACE_F, 8), (FACE_L, 8)),
    ((FACE_D, 8), (FACE_B, 6), (FACE_R, 6)),
    ((FACE_D, 6), (FACE_B, 8), (FACE_L, 6)),
]


def heuristic(state: Dict[str, List[str]]) -> int:
    misplaced_edges = 0
    for (f1, i1), (f2, i2) in EDGES:
        c1 = state[f1][i1]
        c2 = state[f2][i2]
        s1 = SOLVED_STATE[f1][i1]
        s2 = SOLVED_STATE[f2][i2]
        if not ((c1 == s1 and c2 == s2) or (c1 == s2 and c2 == s1)):
            misplaced_edges += 1

    misplaced_corners = 0
    for (f1, i1), (f2, i2), (f3, i3) in CORNERS:
        c = (state[f1][i1], state[f2][i2], state[f3][i3])
        s = (SOLVED_STATE[f1][i1], SOLVED_STATE[f2][i2], SOLVED_STATE[f3][i3])
        if c not in [
            s,
            (s[0], s[2], s[1]),
            (s[1], s[0], s[2]),
            (s[1], s[2], s[0]),
            (s[2], s[0], s[1]),
            (s[2], s[1], s[0]),
        ]:
            misplaced_corners += 1

    displaced = 0
    for face in ALL_FACES:
        center = state[face][4]
        for i in range(9):
            if i != 4 and state[face][i] != center:
                displaced += 1

    return max(misplaced_edges, misplaced_corners * 2, displaced // 8)
