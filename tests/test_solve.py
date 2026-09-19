import pytest

from src.pipeline.solve import (
    Board,
    BeamSearchSolver,
    GreedySolver,
    SmallestFirstSolver,
    find_moves,
    make_solver,
)


def make_board(rows, cols, digits):
    return Board.from_digits(digits, rows, cols)


def test_query_sums_and_counts_nonempty_cells():
    board = make_board(2, 2, [1, 2, 3, 4])
    total, count = board.query((1, 1, 2, 2))
    assert total == 10
    assert count == 4


def test_query_ignores_cleared_cells():
    board = make_board(1, 3, [4, 0, 6])
    total, count = board.query((1, 1, 1, 3))
    assert total == 10
    assert count == 2


def test_clear_zeroes_out_rect():
    board = make_board(1, 3, [4, 6, 9])
    board.clear((1, 1, 1, 2))
    assert board.grid[1][1] == 0
    assert board.grid[1][2] == 0
    assert board.grid[1][3] == 9


def test_is_solved():
    board = make_board(1, 2, [5, 5])
    assert not board.is_solved()
    board.clear((1, 1, 1, 2))
    assert board.is_solved()


def test_finds_a_pair_summing_to_ten():
    board = Board.from_digits([4, 6, 1, 1], rows=2, cols=2)
    solver = GreedySolver()

    move = solver.next_move(board)

    assert move is not None
    total, _ = board.query(move.rect)
    assert total == 10


def test_returns_none_once_board_is_clear():
    board = Board.from_digits([0, 0, 0, 0], rows=2, cols=2)
    solver = GreedySolver()

    assert solver.next_move(board) is None


def test_solve_loop_clears_a_full_board():
    board = Board.from_digits([4, 6, 2, 8], rows=2, cols=2)
    solver = GreedySolver()

    moves = 0
    while True:
        move = solver.next_move(board)
        if move is None:
            break
        board.clear(move.rect)
        moves += 1
        assert moves < 10  # guard against infinite loop

    assert board.is_solved()


def play_out(solver, board):
    """Plays until the solver stops, checking every move really sums to 10."""
    while True:
        move = solver.next_move(board)
        if move is None:
            return
        total, _ = board.query(move.rect)
        assert total == 10
        board.clear(move.rect)


def test_find_moves_returns_each_cell_set_once_smallest_first():
    # 4 6 at the left, empty margin column, then 5 5: two pairs, plus a 4-cell span across them
    board = make_board(1, 5, [4, 6, 0, 5, 5])
    moves = find_moves(board.grid, 1, 5)
    assert [(count, rect) for count, _area, rect in moves] == [(2, (1, 1, 1, 2)), (2, (1, 4, 1, 5))]


def test_smallest_first_prefers_pair_over_larger_rectangle():
    # 1+2+3+4=10 (four cells) comes first in scan order, but 5+5 clears fewer cells.
    board = make_board(1, 6, [1, 2, 3, 4, 5, 5])
    assert GreedySolver(initial_threshold=4).next_move(board).rect == (1, 1, 1, 4)
    assert SmallestFirstSolver().next_move(board).rect == (1, 5, 1, 6)


def test_beam_search_clears_at_least_as_much_as_smallest_first():
    digits = [9, 1, 5, 2, 4, 7, 9, 3, 8, 1, 6, 4, 1, 8, 3, 4, 9, 4, 6, 4] * 2
    smallest_board = make_board(4, 10, digits)
    beam_board = make_board(4, 10, digits)

    play_out(SmallestFirstSolver(), smallest_board)
    play_out(BeamSearchSolver(beam_width=10, branching=4), beam_board)

    assert beam_board.remaining_cells() <= smallest_board.remaining_cells()


def test_remaining_cells_counts_cells_not_digit_values():
    board = make_board(2, 2, [9, 9, 9, 9])  # digit values add up to 36, but only 4 cells
    assert board.remaining_cells() == 4
    board.clear((1, 1, 1, 2))
    assert board.remaining_cells() == 2


def test_beam_search_replans_when_board_changes_unexpectedly():
    solver = BeamSearchSolver(beam_width=5, branching=3)
    board = make_board(2, 2, [4, 6, 2, 8])
    solver.next_move(board)

    fresh = make_board(2, 2, [1, 9, 3, 7])  # a different game: plan no longer applies
    move = solver.next_move(fresh)
    assert fresh.query(move.rect)[0] == 10


def test_beam_search_returns_none_when_no_moves():
    assert BeamSearchSolver().next_move(make_board(1, 2, [1, 1])) is None


def test_make_solver_picks_by_name():
    assert isinstance(make_solver("greedy"), GreedySolver)
    assert isinstance(make_solver("smallest"), SmallestFirstSolver)
    assert isinstance(make_solver("beam", 7, 3), BeamSearchSolver)
    with pytest.raises(ValueError, match="Unknown solver"):
        make_solver("nope")
