from src.board import Board
from src.solver import GreedySolver


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
