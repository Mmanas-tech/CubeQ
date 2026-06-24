from copy import deepcopy
from typing import Dict, List

FACE_U = 'U'
FACE_D = 'D'
FACE_F = 'F'
FACE_B = 'B'
FACE_L = 'L'
FACE_R = 'R'

ALL_FACES = [FACE_U, FACE_R, FACE_F, FACE_D, FACE_L, FACE_B]

SOLVED_STATE = {
    FACE_U: ['W'] * 9,
    FACE_D: ['Y'] * 9,
    FACE_F: ['G'] * 9,
    FACE_B: ['B'] * 9,
    FACE_L: ['O'] * 9,
    FACE_R: ['R'] * 9,
}

COLORS = ['W', 'Y', 'R', 'O', 'B', 'G']


def create_solved():
    return {face: list(colors) for face, colors in SOLVED_STATE.items()}


def clone_state(state):
    return {face: list(stickers) for face, stickers in state.items()}


def _rotate_cw(face):
    return [
        face[6], face[3], face[0],
        face[7], face[4], face[1],
        face[8], face[5], face[2],
    ]


def _rotate_ccw(face):
    return [
        face[2], face[5], face[8],
        face[1], face[4], face[7],
        face[0], face[3], face[6],
    ]


def _rotate_180(face):
    return [
        face[8], face[7], face[6],
        face[5], face[4], face[3],
        face[2], face[1], face[0],
    ]


def move_r(state):
    s = clone_state(state)
    s[FACE_R] = _rotate_ccw(state[FACE_R])
    s[FACE_F][2], s[FACE_F][5], s[FACE_F][8] = state[FACE_U][2], state[FACE_U][5], state[FACE_U][8]
    s[FACE_D][2], s[FACE_D][5], s[FACE_D][8] = state[FACE_F][2], state[FACE_F][5], state[FACE_F][8]
    s[FACE_B][0], s[FACE_B][3], s[FACE_B][6] = state[FACE_D][8], state[FACE_D][5], state[FACE_D][2]
    s[FACE_U][2], s[FACE_U][5], s[FACE_U][8] = state[FACE_B][6], state[FACE_B][3], state[FACE_B][0]
    return s


def move_r_prime(state):
    s = clone_state(state)
    s[FACE_R] = _rotate_cw(state[FACE_R])
    s[FACE_B][6], s[FACE_B][3], s[FACE_B][0] = state[FACE_U][2], state[FACE_U][5], state[FACE_U][8]
    s[FACE_U][2], s[FACE_U][5], s[FACE_U][8] = state[FACE_F][2], state[FACE_F][5], state[FACE_F][8]
    s[FACE_F][2], s[FACE_F][5], s[FACE_F][8] = state[FACE_D][2], state[FACE_D][5], state[FACE_D][8]
    s[FACE_D][2], s[FACE_D][5], s[FACE_D][8] = state[FACE_B][6], state[FACE_B][3], state[FACE_B][0]
    return s


def move_r2(state):
    s = clone_state(state)
    s[FACE_R] = _rotate_180(state[FACE_R])
    s[FACE_D][2], s[FACE_D][5], s[FACE_D][8] = state[FACE_U][2], state[FACE_U][5], state[FACE_U][8]
    s[FACE_U][2], s[FACE_U][5], s[FACE_U][8] = state[FACE_D][2], state[FACE_D][5], state[FACE_D][8]
    s[FACE_B][0], s[FACE_B][3], s[FACE_B][6] = state[FACE_F][8], state[FACE_F][5], state[FACE_F][2]
    s[FACE_F][2], s[FACE_F][5], s[FACE_F][8] = state[FACE_B][6], state[FACE_B][3], state[FACE_B][0]
    return s


def move_l(state):
    s = clone_state(state)
    s[FACE_L] = _rotate_cw(state[FACE_L])
    s[FACE_F][0], s[FACE_F][3], s[FACE_F][6] = state[FACE_U][0], state[FACE_U][3], state[FACE_U][6]
    s[FACE_D][0], s[FACE_D][3], s[FACE_D][6] = state[FACE_F][0], state[FACE_F][3], state[FACE_F][6]
    s[FACE_B][8], s[FACE_B][5], s[FACE_B][2] = state[FACE_D][0], state[FACE_D][3], state[FACE_D][6]
    s[FACE_U][0], s[FACE_U][3], s[FACE_U][6] = state[FACE_B][8], state[FACE_B][5], state[FACE_B][2]
    return s


def move_l_prime(state):
    s = clone_state(state)
    s[FACE_L] = _rotate_ccw(state[FACE_L])
    s[FACE_B][8], s[FACE_B][5], s[FACE_B][2] = state[FACE_U][0], state[FACE_U][3], state[FACE_U][6]
    s[FACE_U][0], s[FACE_U][3], s[FACE_U][6] = state[FACE_F][0], state[FACE_F][3], state[FACE_F][6]
    s[FACE_F][0], s[FACE_F][3], s[FACE_F][6] = state[FACE_D][0], state[FACE_D][3], state[FACE_D][6]
    s[FACE_D][0], s[FACE_D][3], s[FACE_D][6] = state[FACE_B][8], state[FACE_B][5], state[FACE_B][2]
    return s


def move_l2(state):
    s = clone_state(state)
    s[FACE_L] = _rotate_180(state[FACE_L])
    s[FACE_D][0], s[FACE_D][3], s[FACE_D][6] = state[FACE_U][0], state[FACE_U][3], state[FACE_U][6]
    s[FACE_U][0], s[FACE_U][3], s[FACE_U][6] = state[FACE_D][0], state[FACE_D][3], state[FACE_D][6]
    s[FACE_F][0], s[FACE_F][3], s[FACE_F][6] = state[FACE_B][8], state[FACE_B][5], state[FACE_B][2]
    s[FACE_B][8], s[FACE_B][5], s[FACE_B][2] = state[FACE_F][0], state[FACE_F][3], state[FACE_F][6]
    return s


def move_u(state):
    s = clone_state(state)
    s[FACE_U] = _rotate_ccw(state[FACE_U])
    s[FACE_F][0], s[FACE_F][1], s[FACE_F][2] = state[FACE_L][0], state[FACE_L][1], state[FACE_L][2]
    s[FACE_R][0], s[FACE_R][1], s[FACE_R][2] = state[FACE_F][0], state[FACE_F][1], state[FACE_F][2]
    s[FACE_B][0], s[FACE_B][1], s[FACE_B][2] = state[FACE_R][0], state[FACE_R][1], state[FACE_R][2]
    s[FACE_L][0], s[FACE_L][1], s[FACE_L][2] = state[FACE_B][0], state[FACE_B][1], state[FACE_B][2]
    return s


def move_u_prime(state):
    s = clone_state(state)
    s[FACE_U] = _rotate_cw(state[FACE_U])
    s[FACE_F][0], s[FACE_F][1], s[FACE_F][2] = state[FACE_R][0], state[FACE_R][1], state[FACE_R][2]
    s[FACE_L][0], s[FACE_L][1], s[FACE_L][2] = state[FACE_F][0], state[FACE_F][1], state[FACE_F][2]
    s[FACE_B][0], s[FACE_B][1], s[FACE_B][2] = state[FACE_L][0], state[FACE_L][1], state[FACE_L][2]
    s[FACE_R][0], s[FACE_R][1], s[FACE_R][2] = state[FACE_B][0], state[FACE_B][1], state[FACE_B][2]
    return s


def move_u2(state):
    s = clone_state(state)
    s[FACE_U] = _rotate_180(state[FACE_U])
    s[FACE_F][0], s[FACE_F][1], s[FACE_F][2] = state[FACE_B][0], state[FACE_B][1], state[FACE_B][2]
    s[FACE_L][0], s[FACE_L][1], s[FACE_L][2] = state[FACE_R][0], state[FACE_R][1], state[FACE_R][2]
    s[FACE_B][0], s[FACE_B][1], s[FACE_B][2] = state[FACE_F][0], state[FACE_F][1], state[FACE_F][2]
    s[FACE_R][0], s[FACE_R][1], s[FACE_R][2] = state[FACE_L][0], state[FACE_L][1], state[FACE_L][2]
    return s


def move_d(state):
    s = clone_state(state)
    s[FACE_D] = _rotate_ccw(state[FACE_D])
    s[FACE_F][6], s[FACE_F][7], s[FACE_F][8] = state[FACE_R][6], state[FACE_R][7], state[FACE_R][8]
    s[FACE_L][6], s[FACE_L][7], s[FACE_L][8] = state[FACE_F][6], state[FACE_F][7], state[FACE_F][8]
    s[FACE_B][6], s[FACE_B][7], s[FACE_B][8] = state[FACE_L][6], state[FACE_L][7], state[FACE_L][8]
    s[FACE_R][6], s[FACE_R][7], s[FACE_R][8] = state[FACE_B][6], state[FACE_B][7], state[FACE_B][8]
    return s


def move_d_prime(state):
    s = clone_state(state)
    s[FACE_D] = _rotate_cw(state[FACE_D])
    s[FACE_F][6], s[FACE_F][7], s[FACE_F][8] = state[FACE_L][6], state[FACE_L][7], state[FACE_L][8]
    s[FACE_L][6], s[FACE_L][7], s[FACE_L][8] = state[FACE_B][6], state[FACE_B][7], state[FACE_B][8]
    s[FACE_B][6], s[FACE_B][7], s[FACE_B][8] = state[FACE_R][6], state[FACE_R][7], state[FACE_R][8]
    s[FACE_R][6], s[FACE_R][7], s[FACE_R][8] = state[FACE_F][6], state[FACE_F][7], state[FACE_F][8]
    return s


def move_d2(state):
    s = clone_state(state)
    s[FACE_D] = _rotate_180(state[FACE_D])
    s[FACE_F][6], s[FACE_F][7], s[FACE_F][8] = state[FACE_B][6], state[FACE_B][7], state[FACE_B][8]
    s[FACE_L][6], s[FACE_L][7], s[FACE_L][8] = state[FACE_R][6], state[FACE_R][7], state[FACE_R][8]
    s[FACE_B][6], s[FACE_B][7], s[FACE_B][8] = state[FACE_F][6], state[FACE_F][7], state[FACE_F][8]
    s[FACE_R][6], s[FACE_R][7], s[FACE_R][8] = state[FACE_L][6], state[FACE_L][7], state[FACE_L][8]
    return s


def move_f(state):
    s = clone_state(state)
    s[FACE_F] = _rotate_cw(state[FACE_F])
    s[FACE_R][0], s[FACE_R][3], s[FACE_R][6] = state[FACE_U][6], state[FACE_U][7], state[FACE_U][8]
    s[FACE_D][0], s[FACE_D][1], s[FACE_D][2] = state[FACE_R][6], state[FACE_R][3], state[FACE_R][0]
    s[FACE_L][2], s[FACE_L][5], s[FACE_L][8] = state[FACE_D][0], state[FACE_D][1], state[FACE_D][2]
    s[FACE_U][6], s[FACE_U][7], s[FACE_U][8] = state[FACE_L][8], state[FACE_L][5], state[FACE_L][2]
    return s


def move_f_prime(state):
    s = clone_state(state)
    s[FACE_F] = _rotate_ccw(state[FACE_F])
    s[FACE_L][2], s[FACE_L][5], s[FACE_L][8] = state[FACE_U][8], state[FACE_U][7], state[FACE_U][6]
    s[FACE_U][6], s[FACE_U][7], s[FACE_U][8] = state[FACE_R][0], state[FACE_R][3], state[FACE_R][6]
    s[FACE_R][0], s[FACE_R][3], s[FACE_R][6] = state[FACE_D][2], state[FACE_D][1], state[FACE_D][0]
    s[FACE_D][0], s[FACE_D][1], s[FACE_D][2] = state[FACE_L][2], state[FACE_L][5], state[FACE_L][8]
    return s


def move_f2(state):
    s = clone_state(state)
    s[FACE_F] = _rotate_180(state[FACE_F])
    s[FACE_U][6], s[FACE_U][7], s[FACE_U][8] = state[FACE_D][2], state[FACE_D][1], state[FACE_D][0]
    s[FACE_R][0], s[FACE_R][3], s[FACE_R][6] = state[FACE_L][8], state[FACE_L][5], state[FACE_L][2]
    s[FACE_D][0], s[FACE_D][1], s[FACE_D][2] = state[FACE_U][8], state[FACE_U][7], state[FACE_U][6]
    s[FACE_L][2], s[FACE_L][5], s[FACE_L][8] = state[FACE_R][6], state[FACE_R][3], state[FACE_R][0]
    return s


def move_b(state):
    s = clone_state(state)
    s[FACE_B] = _rotate_cw(state[FACE_B])
    s[FACE_L][6], s[FACE_L][3], s[FACE_L][0] = state[FACE_U][0], state[FACE_U][1], state[FACE_U][2]
    s[FACE_D][6], s[FACE_D][7], s[FACE_D][8] = state[FACE_L][0], state[FACE_L][3], state[FACE_L][6]
    s[FACE_R][2], s[FACE_R][5], s[FACE_R][8] = state[FACE_D][8], state[FACE_D][7], state[FACE_D][6]
    s[FACE_U][0], s[FACE_U][1], s[FACE_U][2] = state[FACE_R][2], state[FACE_R][5], state[FACE_R][8]
    return s


def move_b_prime(state):
    s = clone_state(state)
    s[FACE_B] = _rotate_ccw(state[FACE_B])
    s[FACE_R][2], s[FACE_R][5], s[FACE_R][8] = state[FACE_U][0], state[FACE_U][1], state[FACE_U][2]
    s[FACE_D][6], s[FACE_D][7], s[FACE_D][8] = state[FACE_R][8], state[FACE_R][5], state[FACE_R][2]
    s[FACE_L][0], s[FACE_L][3], s[FACE_L][6] = state[FACE_D][6], state[FACE_D][7], state[FACE_D][8]
    s[FACE_U][0], s[FACE_U][1], s[FACE_U][2] = state[FACE_L][6], state[FACE_L][3], state[FACE_L][0]
    return s


def move_b2(state):
    s = clone_state(state)
    s[FACE_B] = _rotate_180(state[FACE_B])
    s[FACE_U][0], s[FACE_U][1], s[FACE_U][2] = state[FACE_D][8], state[FACE_D][7], state[FACE_D][6]
    s[FACE_L][0], s[FACE_L][3], s[FACE_L][6] = state[FACE_R][8], state[FACE_R][5], state[FACE_R][2]
    s[FACE_D][6], s[FACE_D][7], s[FACE_D][8] = state[FACE_U][2], state[FACE_U][1], state[FACE_U][0]
    s[FACE_R][8], s[FACE_R][5], s[FACE_R][2] = state[FACE_L][0], state[FACE_L][3], state[FACE_L][6]
    return s


MOVES = {
    'R': move_r, "R'": move_r_prime, 'R2': move_r2,
    'L': move_l, "L'": move_l_prime, 'L2': move_l2,
    'U': move_u, "U'": move_u_prime, 'U2': move_u2,
    'D': move_d, "D'": move_d_prime, 'D2': move_d2,
    'F': move_f, "F'": move_f_prime, 'F2': move_f2,
    'B': move_b, "B'": move_b_prime, 'B2': move_b2,
}

OPPOSITE_MOVES = {
    'R': "R'", "R'": 'R', 'R2': 'R2',
    'L': "L'", "L'": 'L', 'L2': 'L2',
    'U': "U'", "U'": 'U', 'U2': 'U2',
    'D': "D'", "D'": 'D', 'D2': 'D2',
    'F': "F'", "F'": 'F', 'F2': 'F2',
    'B': "B'", "B'": 'B', 'B2': 'B2',
}

FACE_ORDER = ['R', 'L', 'U', 'D', 'F', 'B']


def get_face(move_name):
    return move_name[0]


def apply_move(state, move_name):
    return MOVES[move_name](state)


def apply_moves(state, moves):
    current = state
    for m in moves:
        current = apply_move(current, m)
    return current


def is_solved(state):
    for face in ALL_FACES:
        stickers = state[face]
        if not all(s == stickers[0] for s in stickers):
            return False
    return True


def state_to_tuple(state):
    return ''.join(state[face][i] for face in ALL_FACES for i in range(9))


def count_displaced_stickers(state):
    count = 0
    for face in ALL_FACES:
        center = state[face][4]
        for i in range(9):
            if i != 4 and state[face][i] != center:
                count += 1
    return count


def scramble(num_moves=20, seed=None):
    import random
    rng = random.Random(seed)
    moves_list = list(MOVES.keys())
    result = []
    last_face = None
    second_last_face = None
    for _ in range(num_moves):
        while True:
            m = rng.choice(moves_list)
            f = get_face(m)
            if f == last_face:
                continue
            if f == second_last_face and OPPOSITE_MOVES.get(m) == result[-1]:
                continue
            break
        result.append(m)
        second_last_face = last_face
        last_face = f
    return apply_moves(create_solved(), result), result


# --- Fast flat-state representation ---
# State is a 54-element list: U0..U8, R0..R8, F0..F8, D0..D8, L0..L8, B0..B8
# Each sticker is encoded as an integer 0-5 (W=0, Y=1, R=2, O=3, B=4, G=5)

_COLOR_TO_INT = {'W': 0, 'Y': 1, 'R': 2, 'O': 3, 'B': 4, 'G': 5}
_INT_TO_COLOR = {0: 'W', 1: 'Y', 2: 'R', 3: 'O', 4: 'B', 5: 'G'}
_FACE_OFFSET = {'U': 0, 'R': 9, 'F': 18, 'D': 27, 'L': 36, 'B': 45}


def state_to_flat(state):
    flat = [0] * 54
    for face, offset in _FACE_OFFSET.items():
        for i in range(9):
            flat[offset + i] = _COLOR_TO_INT[state[face][i]]
    return flat


def flat_to_state(flat):
    state = {}
    for face, offset in _FACE_OFFSET.items():
        state[face] = [_INT_TO_COLOR[flat[offset + i]] for i in range(9)]
    return state


def _build_move_perms():
    solved = create_solved()
    perms = {}
    for move_name in MOVES:
        new_state = apply_move(solved, move_name)
        flat_solved = state_to_flat(solved)
        flat_new = state_to_flat(new_state)
        perm = [0] * 54
        for i in range(54):
            val = flat_solved[i]
            for j in range(54):
                if flat_new[j] == val and j not in perm:
                    perm[j] = i
                    break
        perms[move_name] = perm
    return perms


def _build_perms_from_example():
    solved = state_to_flat(create_solved())
    perms = {}
    for move_name in MOVES:
        new_state = apply_move(create_solved(), move_name)
        flat_new = state_to_flat(new_state)
        perm = [0] * 54
        for to_idx in range(54):
            val = flat_new[to_idx]
            for from_idx in range(54):
                if solved[from_idx] == val:
                    if from_idx not in perm:
                        perm[to_idx] = from_idx
                        break
        perms[move_name] = perm
    return perms


# Precompute move permutations: perm[i] = source index
# new_flat[i] = old_flat[perm[i]]
_MOVE_PERMS = None


def _ensure_move_perms():
    global _MOVE_PERMS
    if _MOVE_PERMS is not None:
        return
    _MOVE_PERMS = _build_perms_from_example()


def apply_move_flat(flat, move_name):
    perm = _MOVE_PERMS[move_name]
    return [flat[perm[i]] for i in range(54)]


def is_solved_flat(flat):
    for offset in range(0, 54, 9):
        c = flat[offset]
        for i in range(1, 9):
            if flat[offset + i] != c:
                return False
    return True
