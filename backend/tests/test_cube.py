import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.cube import (
    create_solved, is_solved, state_to_tuple, apply_move, apply_moves,
    MOVES, scramble, count_displaced_stickers,
    move_r, move_r_prime, move_r2,
    move_l, move_l_prime, move_l2,
    move_u, move_u_prime, move_u2,
    move_d, move_d_prime, move_d2,
    move_f, move_f_prime, move_f2,
    move_b, move_b_prime, move_b2,
)


def test_solved_state():
    state = create_solved()
    assert is_solved(state)
    assert len(state) == 6
    for face in state:
        assert len(state[face]) == 9


def test_solved_state_colors():
    state = create_solved()
    assert state['U'] == ['W'] * 9
    assert state['D'] == ['Y'] * 9
    assert state['F'] == ['G'] * 9
    assert state['B'] == ['B'] * 9
    assert state['L'] == ['O'] * 9
    assert state['R'] == ['R'] * 9


def test_single_move_not_solved():
    state = create_solved()
    for move_name in MOVES:
        result = apply_move(state, move_name)
        assert not is_solved(result), f"Move {move_name} on solved state should not be solved"


def test_move_inverse():
    state = create_solved()
    scrambled, moves_list = scramble(20, seed=42)
    from core.cube import OPPOSITE_MOVES
    inverse = []
    for m in reversed(moves_list):
        inverse.append(OPPOSITE_MOVES[m])
    result = apply_moves(scrambled, inverse)
    assert is_solved(result), "Applying inverse of scramble should return to solved"


def test_move_cancellation():
    state = create_solved()
    for move_name in MOVES:
        result = apply_move(state, move_name)
        # Find inverse
        for inv_name in MOVES:
            if MOVES[inv_name](result) == state:
                break
        else:
            assert False, f"No inverse found for {move_name}"


def test_r_four_times():
    state = create_solved()
    result = state
    for _ in range(4):
        result = move_r(result)
    assert is_solved(result), "R applied 4 times should return to solved"


def test_l_four_times():
    state = create_solved()
    result = state
    for _ in range(4):
        result = move_l(result)
    assert is_solved(result), "L applied 4 times should return to solved"


def test_u_four_times():
    state = create_solved()
    result = state
    for _ in range(4):
        result = move_u(result)
    assert is_solved(result), "U applied 4 times should return to solved"


def test_d_four_times():
    state = create_solved()
    result = state
    for _ in range(4):
        result = move_d(result)
    assert is_solved(result), "D applied 4 times should return to solved"


def test_f_four_times():
    state = create_solved()
    result = state
    for _ in range(4):
        result = move_f(result)
    assert is_solved(result), "F applied 4 times should return to solved"


def test_b_four_times():
    state = create_solved()
    result = state
    for _ in range(4):
        result = move_b(result)
    assert is_solved(result), "B applied 4 times should return to solved"


def test_r_r_prime():
    state = create_solved()
    result = move_r(state)
    result = move_r_prime(result)
    assert is_solved(result), "R then R' should return to solved"


def test_l_l_prime():
    state = create_solved()
    result = move_l(state)
    result = move_l_prime(result)
    assert is_solved(result), "L then L' should return to solved"


def test_u_u_prime():
    state = create_solved()
    result = move_u(state)
    result = move_u_prime(result)
    assert is_solved(result), "U then U' should return to solved"


def test_d_d_prime():
    state = create_solved()
    result = move_d(state)
    result = move_d_prime(result)
    assert is_solved(result), "D then D' should return to solved"


def test_f_f_prime():
    state = create_solved()
    result = move_f(state)
    result = move_f_prime(result)
    assert is_solved(result), "F then F' should return to solved"


def test_b_b_prime():
    state = create_solved()
    result = move_b(state)
    result = move_b_prime(result)
    assert is_solved(result), "B then B' should return to solved"


def test_r2_twice():
    state = create_solved()
    result = move_r2(state)
    result = move_r2(result)
    assert is_solved(result), "R2 applied twice should return to solved"


def test_all_x2_equals_xx():
    base_state = apply_move(create_solved(), 'U')
    for move_name in ['R2', 'L2', 'U2', 'D2', 'F2', 'B2']:
        base_face = move_name[0]
        result_xx = apply_move(apply_move(base_state, base_face), base_face)
        result_x2 = apply_move(base_state, move_name)
        assert result_xx == result_x2, f"{move_name} != {base_face}{base_face} on non-trivial state"


def test_scramble_produces_moves():
    state, moves_list = scramble(20, seed=42)
    assert len(moves_list) == 20
    assert not is_solved(state)


def test_scramble_inverse():
    state, moves_list = scramble(10, seed=123)
    from core.cube import OPPOSITE_MOVES
    inverse = []
    for m in reversed(moves_list):
        inverse.append(OPPOSITE_MOVES[m])
    result = apply_moves(state, inverse)
    assert is_solved(result)


def test_state_to_tuple_hashable():
    state = create_solved()
    t = state_to_tuple(state)
    assert isinstance(t, tuple)
    d = {t: "solved"}
    assert d[t] == "solved"


def test_count_displaced_solved():
    state = create_solved()
    assert count_displaced_stickers(state) == 0


def test_count_displaced_after_move():
    state = create_solved()
    result = move_r(state)
    count = count_displaced_stickers(result)
    assert count > 0


def test_all_18_moves_exist():
    expected = [
        'R', "R'", 'R2',
        'L', "L'", 'L2',
        'U', "U'", 'U2',
        'D', "D'", 'D2',
        'F', "F'", 'F2',
        'B', "B'", 'B2',
    ]
    for m in expected:
        assert m in MOVES, f"Move {m} not found in MOVES"


def test_apply_moves_sequence():
    state = create_solved()
    moves = ['R', 'U', "R'", "U'"]
    result = apply_moves(state, moves)
    assert not is_solved(result)


def test_t_perm():
    state = create_solved()
    moves = ['R', 'U', "R'", "U'", "R'", 'F', 'R', 'R', "U'", "R'", "U'", 'R', 'U', "R'", "F'"]
    result = apply_moves(state, moves)
    assert not is_solved(result)
    from core.cube import OPPOSITE_MOVES
    inverse = [OPPOSITE_MOVES[m] for m in reversed(moves)]
    result2 = apply_moves(result, inverse)
    assert is_solved(result2)


def test_superflip():
    state = create_solved()
    superflip = [
        'U', 'R', 'R', 'F', 'F', 'D', 'R', 'B', 'B',
        'U', 'U', 'L', 'L', 'B', 'B', 'D', 'D', 'F', 'F', 'R',
    ]
    result = apply_moves(state, superflip)
    assert not is_solved(result)
