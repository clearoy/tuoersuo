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


# Attempt 1 uses the configured mouse timing; attempt 2 (only if attempt 1 cleared nothing)
# moves and drags this many times slower.
_ATTEMPT_SLOWDOWNS = (1.0, 2.5)


def _play_move(board: Board, tiles: list, geometry, config: Config, move) -> int:
    """Drags the move and confirms on screen that its tiles disappeared. Returns the attempt
    number that worked; raises with diagnostics if none did."""
    cells = board.nonempty_cells(move.rect)
    for attempt, slowdown in enumerate(_ATTEMPT_SLOWDOWNS, start=1):
        execute.execute_move(
            config.window_title,
            tiles,
            move,
            config.cols,
            geometry,
            move_duration=config.move_duration * slowdown,
            drag_duration=config.drag_duration * slowdown,
            settle_delay=config.settle_delay,
        )
        if not config.verify_moves:
            return attempt
        if execute.wait_until_cleared(
            config.window_title, config.capture_crop_percent, tiles, config.cols, cells, config.verify_timeout
        ):
            return attempt

    x1, y1, x2, y2 = move.rect
    image_path = execute.save_failure_image(
        config.window_title, config.capture_crop_percent, tiles, config.cols, cells
    )
    digits = "\n".join(str(board.grid[i][y1 : y2 + 1]) for i in range(x1, x2 + 1))
    raise RuntimeError(
        f"Move {move.rect} cleared nothing after {len(_ATTEMPT_SLOWDOWNS)} attempts.\n"
        f"Digits in that rectangle as the bot read them (0 = already cleared):\n{digits}\n"
        f"Their sum is {board.query(move.rect)[0]} (must be 10 - if not, the board was misread).\n"
        f"{image_path} shows the screen now, with the tiles that should have cleared boxed in red. "
        "If those tiles are already gone, the check itself is off; if they are still there, "
        "the game ignored the drag."
    )


def play(board: Board, tiles: list, geometry, config: Config, solver: Solver) -> int:
    """Runs the solve/execute loop until no moves remain. Returns the number of cells cleared."""
    move_count = 0
    retried = []
    while True:
        move = solver.next_move(board)
        if move is None:
            break
        move_count += 1
        attempts = _play_move(board, tiles, geometry, config, move)
        if attempts > 1:
            x1, y1, x2, y2 = move.rect
            retried.append(move_count)
            print(
                f"Move {move_count} {move.rect} needed {attempts} attempts "
                f"(rectangle {x2 - x1 + 1}x{y2 - y1 + 1}, corner cells {board.grid[x1][y1]} and "
                f"{board.grid[x2][y2]}, 0 = empty)"
            )
        board.clear(move.rect)

    if retried:
        print(f"{len(retried)} of {move_count} moves needed a retry: moves {retried}")
    return config.rows * config.cols - board.remaining_cells()


def run(config: Config, solver: Solver = None) -> int:
    solver = solver or make_solver(config.solver, config.beam_width, config.beam_branching)
    board, tiles, geometry = read_board(config)
    board.show()
    return play(board, tiles, geometry, config, solver)
