from core.cube import create_solved, apply_move, apply_moves, is_solved, scramble
from core.solver import solve, solve_ida_star


def test_solved_returns_empty():
    state = create_solved()
    result = solve(state)
    assert result['success']
    assert result['moves'] == []
    assert result['method'] == 'already_solved'


def test_single_move_r():
    state = create_solved()
    state = apply_move(state, 'R')
    result = solve(state, timeout=5)
    assert result['success'], f"Failed to solve R: {result}"
    final = apply_moves(state, result['moves'])
    assert is_solved(final)


def test_single_move_u():
    state = create_solved()
    state = apply_move(state, 'U')
    result = solve(state, timeout=5)
    assert result['success'], f"Failed to solve U: {result}"
    final = apply_moves(state, result['moves'])
    assert is_solved(final)


def test_two_moves():
    state = create_solved()
    state = apply_moves(state, ['R', 'U'])
    result = solve(state, timeout=5)
    assert result['success'], f"Failed to solve R U: {result}"
    final = apply_moves(state, result['moves'])
    assert is_solved(final)


def test_scramble_solve():
    state, moves = scramble(5, seed=42)
    result = solve(state, timeout=15)
    assert result['success'], f"Failed to solve scramble: {result}"
    final = apply_moves(state, result['moves'])
    assert is_solved(final)


def test_invalid_cube():
    state = create_solved()
    state['U'][0] = 'X'
    result = solve(state)
    assert not result['success']


def test_move_count_reasonable():
    state, _ = scramble(3, seed=7)
    result = solve(state, timeout=10)
    assert result['success']
    assert result['move_count'] <= 12


def test_solve_returns_method():
    state = create_solved()
    result = solve(state)
    assert 'method' in result
    assert 'solve_time' in result or result['method'] == 'already_solved'
