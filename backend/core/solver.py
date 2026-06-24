import time
from typing import Dict, List
from core.cube import (
    create_solved, apply_move, is_solved, MOVES,
    get_face, clone_state, ALL_FACES, state_to_tuple
)
from core.validator import validate_cube

COLOR_MAP = {'W': 'U', 'Y': 'D', 'R': 'R', 'O': 'L', 'B': 'B', 'G': 'F'}

KOC_TO_OUR = {
    "R": "R'", "R'": "R", "R2": "R2",
    "L": "L",  "L'": "L'", "L2": "L2",
    "U": "U'", "U'": "U", "U2": "U2",
    "D": "D'", "D'": "D", "D2": "D2",
    "F": "F",  "F'": "F'", "F2": "F2",
    "B": "B",  "B'": "B'", "B2": "B2",
}


def state_to_facelets(state: Dict[str, List[str]]) -> str:
    return ''.join(COLOR_MAP[state[face][i]] for face in ALL_FACES for i in range(9))


def solve(state: Dict[str, List[str]], timeout: float = 30) -> Dict:
    valid, err = validate_cube(state)
    if not valid:
        return {'success': False, 'error': err, 'moves': [], 'method': None}

    if is_solved(state):
        return {'success': True, 'moves': [], 'method': 'already_solved', 'move_count': 0}

    start_time = time.time()

    try:
        from kociemba.search import Search
        from kociemba.tools import verify

        facelets = state_to_facelets(state)
        v = verify(facelets)
        if v != 0:
            err_map = {
                1: 'Wrong number of stickers per color — please re-check all faces',
                2: 'Edges are in impossible positions — please re-scan or re-enter colors carefully',
                3: 'Corners are in impossible positions — please re-scan or re-enter colors carefully',
                4: 'Edge orientation is impossible — please re-scan or re-enter colors carefully',
                5: 'Corner orientation is impossible — please re-scan or re-enter colors carefully',
                6: 'Parity error — please re-scan or re-enter colors carefully',
            }
            return {'success': False, 'error': err_map.get(v, f'Invalid cube state (error {v}) — please re-scan all faces'),
                    'moves': [], 'method': None}

        sol_str = Search().solution(facelets, maxDepth=25, timeOut=max(1, int(timeout)), useSeparator=False)
        if sol_str is None:
            return {'success': False, 'error': 'kociemba could not find solution',
                    'moves': [], 'method': None}

        koc_moves = sol_str.replace(".", "").split()
        our_moves = [KOC_TO_OUR[t] for t in koc_moves]

        result_state = state
        for m in our_moves:
            result_state = apply_move(result_state, m)
        if not is_solved(result_state):
            return {'success': False, 'error': 'solution verification failed',
                    'moves': [], 'method': None}

        return {
            'success': True,
            'moves': our_moves,
            'method': 'kociemba',
            'move_count': len(our_moves),
            'solve_time': round(time.time() - start_time, 3)
        }
    except Exception as e:
        return {'success': False, 'error': str(e), 'moves': [], 'method': None}
