"""Assembles the four pipeline steps: capture -> ocr -> solve -> execute."""

from src.config import Config
from src.pipeline import capture, execute, ocr
from src.pipeline.solve import Board, Solver, GreedySolver


def read_board(config: Config) -> tuple:
    save_dir = "Images" if config.save_tile_images else None
    tiles = capture.capture(config.window_title, config.capture_crop_percent, config.rows, config.cols, save_dir)

    ocr_client = ocr.OCRClient(config.baidu_api_key, config.baidu_secret_key)
    digits = ocr.recognize_all(tiles, ocr_client, config.ocr_thread_count)

    board = Board.from_digits(digits, config.rows, config.cols)
    return board, tiles


def play(board: Board, tiles: list, config: Config, solver: Solver) -> int:
    """Runs the solve/execute loop until no moves remain. Returns the final score."""
    while True:
        move = solver.next_move(board)
        if move is None:
            break
        execute.execute_move(config.window_title, tiles, move, config.cols)
        board.clear(move.rect)

    return config.rows * config.cols - board.remaining_score()


def run(config: Config, solver: Solver = None) -> int:
    solver = solver or GreedySolver()
    board, tiles = read_board(config)
    board.show()
    return play(board, tiles, config, solver)
