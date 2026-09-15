from src.pipeline.solve import Board, GreedySolver


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
