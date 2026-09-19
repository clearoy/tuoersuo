"""Assembles the four pipeline steps: capture -> ocr -> solve -> execute."""

from src.config import Config
from src.pipeline import capture, execute, ocr
from src.pipeline.solve import Board, Solver, make_solver


def read_board(config: Config) -> tuple:
    image_path, tiles, geometry = capture.capture(
        config.window_title,
        config.capture_crop_percent,
        config.rows,
        config.cols,
        config.board_begin_position,
        config.board_end_margin,
    )

    digits = ocr.recognize_board(image_path, config.rows, config.cols, config.gemini_api_key, config.gemini_model)

    board = Board.from_digits(digits, config.rows, config.cols)
    return board, tiles, geometry


def play(board: Board, tiles: list, geometry, config: Config, solver: Solver) -> int:
    """Runs the solve/execute loop until no moves remain. Returns the number of cells cleared."""
    while True:
        move = solver.next_move(board)
        if move is None:
            break
        execute.execute_move(
            config.window_title,
            tiles,
            move,
            config.cols,
            geometry,
            move_duration=config.move_duration,
            drag_duration=config.drag_duration,
            settle_delay=config.settle_delay,
        )
        board.clear(move.rect)

    return config.rows * config.cols - board.remaining_cells()


def run(config: Config, solver: Solver = None) -> int:
    solver = solver or make_solver(config.solver, config.beam_width, config.beam_branching)
    board, tiles, geometry = read_board(config)
    board.show()
    return play(board, tiles, geometry, config, solver)
