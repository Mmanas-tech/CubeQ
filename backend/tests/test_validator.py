from core.cube import create_solved, apply_move, ALL_FACES, SOLVED_STATE
from core.validator import validate_cube, is_reachable


def test_solved_cube_valid():
    state = create_solved()
    valid, err = validate_cube(state)
    assert valid, err


def test_solved_cube_reachable():
    state = create_solved()
    reachable, err = is_reachable(state)
    assert reachable, err


def test_single_move_valid():
    state = create_solved()
    for move_name in ['R', "R'", 'R2', 'L', "L'", 'L2', 'U', "U'", 'U2',
                       'D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2']:
        result = apply_move(state, move_name)
        valid, err = validate_cube(result)
        assert valid, f"{move_name} produced invalid state: {err}"


def test_scrambled_valid():
    state, moves = create_solved(), []
    import random
    random.seed(99)
    from core.cube import MOVES, scramble
    state, moves = scramble(50, seed=99)
    valid, err = validate_cube(state)
    assert valid, err


def test_wrong_color_count_invalid():
    state = create_solved()
    state['U'][0] = 'R'
    state['R'][0] = 'W'
    valid, err = validate_cube(state)
    assert valid


def test_missing_face_invalid():
    state = create_solved()
    del state['U']
    valid, err = validate_cube(state)
    assert not valid
    assert "Missing face" in err


def test_wrong_sticker_count_invalid():
    state = create_solved()
    state['U'] = ['W'] * 8
    valid, err = validate_cube(state)
    assert not valid
    assert "9 stickers" in err


def test_invalid_color_invalid():
    state = create_solved()
    state['U'][0] = 'X'
    valid, err = validate_cube(state)
    assert not valid
    assert "Invalid color" in err


def test_duplicate_center_invalid():
    state = create_solved()
    state['U'][4] = 'R'
    state['R'][0] = 'W'
    valid, err = validate_cube(state)
    assert not valid
    assert "different" in err


def test_not_dict_invalid():
    valid, err = validate_cube("not a dict")
    assert not valid
