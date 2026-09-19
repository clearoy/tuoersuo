"""Step 4: turn a Move into real mouse input against the live game window.

The mini-program board runs in a webview/canvas, which needs real mousemove/mousedown/
mouseup events spaced out in time to register a drag - teleporting the cursor and
firing click+drag back-to-back gets missed or misread. So this moves smoothly to the
start tile, pauses, clicks, drags slowly, then lets the game settle before returning.
"""

import time

import pyautogui
from PIL import ImageDraw

from src.pipeline import capture
from src.pipeline.capture import CaptureGeometry, Tile, get_window_bounds
from src.pipeline.solve import Move

# pyautogui sleeps 0.1s after every call by default (3 calls per move = 0.3s wasted).
pyautogui.PAUSE = 0.01


def tile_center(tile: Tile) -> tuple:
    cx = (tile.position[0] + tile.position[2]) / 2
    cy = (tile.position[1] + tile.position[3]) / 2
    return cx, cy


def execute_move(
    window_title: str,
    tiles: list[Tile],
    move: Move,
    cols: int,
    geometry: CaptureGeometry,
    move_duration: float = 0.05,
    drag_duration: float = 0.15,
    settle_delay: float = 0.08,
) -> None:
    x1, y1, x2, y2 = move.rect
    tile_a = tiles[(x1 - 1) * cols + (y1 - 1)]
    tile_b = tiles[(x2 - 1) * cols + (y2 - 1)]

    # Re-fetch the window position each move in case it moved since capture.
    left, top, _width, _height = get_window_bounds(window_title)
    start_x, start_y = geometry.to_screen_point(left, top, *tile_center(tile_a))
    end_x, end_y = geometry.to_screen_point(left, top, *tile_center(tile_b))

    pyautogui.moveTo(start_x, start_y, duration=move_duration)
    pyautogui.click(start_x, start_y, button="left")
    time.sleep(0.03)
    pyautogui.dragTo(end_x, end_y, duration=drag_duration, button="left")
    time.sleep(settle_delay)


# A tile is a white square with a dark digit in the middle. Sampling to the left/right and
# above/below the digit (as a fraction of the cell size) hits only white tile or, once the
# tile is cleared, only the green board.
_SAMPLE_OFFSETS = ((-0.28, 0), (0.28, 0), (0, -0.28), (0, 0.28))


def is_tile_present(image, tile: Tile) -> bool:
    x1, y1, x2, y2 = tile.position
    cx, cy, width, height = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
    white = 0
    for dx, dy in _SAMPLE_OFFSETS:
        x = min(max(int(cx + dx * width), 0), image.width - 1)
        y = min(max(int(cy + dy * height), 0), image.height - 1)
        r, g, b = image.getpixel((x, y))[:3]
        if r > 200 and g > 200 and b > 200:
            white += 1
    return white >= 3


def _tile_for(tiles: list, cols: int, cell: tuple) -> Tile:
    row, col = cell
    return tiles[(row - 1) * cols + (col - 1)]


def wait_until_cleared(
    window_title: str,
    crop_percent: float,
    tiles: list,
    cols: int,
    cells: list,
    timeout: float = 0.6,
    poll: float = 0.05,
) -> bool:
    """Polls the screen until none of `cells` (row, col) still shows a tile, or timeout."""
    deadline = time.monotonic() + timeout
    while True:
        image, _geometry = capture.grab_board(window_title, crop_percent)
        if not any(is_tile_present(image, _tile_for(tiles, cols, cell)) for cell in cells):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(poll)


def save_failure_image(
    window_title: str,
    crop_percent: float,
    tiles: list,
    cols: int,
    cells: list,
    path: str = "failed_move.png",
) -> str:
    """Saves the current board with a red box around each tile that should have cleared."""
    image, _geometry = capture.grab_board(window_title, crop_percent)
    image = image.convert("RGB")
    draw = ImageDraw.Draw(image)
    for cell in cells:
        draw.rectangle(_tile_for(tiles, cols, cell).position, outline="red", width=3)
    image.save(path)
    return path
