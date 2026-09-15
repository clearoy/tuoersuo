from src.board import Board


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
