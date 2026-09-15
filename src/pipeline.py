"""End-to-end orchestration: capture -> OCR -> solve loop -> play. The solve step is the
only piece meant to change later (swap GreedySolver for an RL-backed Solver)."""

import concurrent.futures

from src.board import Board
from src.capture import WindowCapture
from src.config import Config
from src.controller import GameController
from src.image_processor import ImageProcessor
from src.ocr import OCRClient
from src.solver import Solver, GreedySolver
from src.tile import Tile


def read_board(config: Config) -> tuple:
    """Capture the game window, OCR every tile, and return (board, tiles)."""
    capture = WindowCapture(config.window_title, config.capture_crop_percent)
    image_path = capture.capture()

    processor = ImageProcessor(image_path, config.rows, config.cols)
    save_dir = "Images" if config.save_tile_images else None
    tiles = processor.split_image(save_dir=save_dir)

    ocr = OCRClient(config.baidu_api_key, config.baidu_secret_key)
    digits = _recognize_all(tiles, ocr, config.ocr_thread_count)

    board = Board.from_digits(digits, config.rows, config.cols)
    return board, tiles


def _recognize_all(tiles: list[Tile], ocr: OCRClient, thread_count: int) -> list:
    digits = [0] * len(tiles)

    def recognize(tile: Tile) -> None:
        digits[tile.tile_id] = ocr.recognize_digit(tile.image)

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = {executor.submit(recognize, tile): tile for tile in tiles}
        for future in concurrent.futures.as_completed(futures):
            future.result()

    return digits


def play(board: Board, tiles: list, config: Config, solver: Solver) -> int:
    """Runs the solve/execute loop until no moves remain. Returns the final score."""
    controller = GameController(config.window_title)

    while True:
        move = solver.next_move(board)
        if move is None:
            break
        controller.execute_move(tiles, move, config.cols)
        board.clear(move.rect)

    return config.rows * config.cols - board.remaining_score()


def run(config: Config, solver: Solver = None) -> int:
    solver = solver or GreedySolver()
    board, tiles = read_board(config)
    board.show()
    score = play(board, tiles, config, solver)
    return score
