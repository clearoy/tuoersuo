"""Step 1: find the game window, screenshot its board, and compute each cell's pixel position.

No per-tile image cropping happens here: OCR (step 2) reads the whole board image in one
call, so this step only needs cell geometry, used later for click targeting in step 4.
"""

from dataclasses import dataclass

import pyautogui
import pygetwindow as gw
from PIL import Image


@dataclass
class Tile:
    position: tuple  # (x1, y1, x2, y2) pixel bbox within the captured screenshot
    tile_id: int


def get_window(window_title: str):
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        raise RuntimeError(f"No window found with title '{window_title}'")
    return windows[0]


def _crop_bottom(image_path: str, percent_to_keep: float) -> None:
    image = Image.open(image_path)
    width, height = image.size
    kept_height = int(height * percent_to_keep)
    cropped = image.crop((0, height - kept_height, width, height))
    cropped.save(image_path)


def screenshot_board(window_title: str, crop_percent: float, image_path: str = "screenshot.png") -> str:
    window = get_window(window_title)
    image = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    image.save(image_path, "PNG")
    _crop_bottom(image_path, crop_percent)
    return image_path


def compute_tile_positions(
    image_path: str,
    rows: int,
    cols: int,
    begin_position=(15, 15),
    delta=(10, 10, 40, 40),
) -> list[Tile]:
    width, height = Image.open(image_path).size
    height = height // (rows + 1) * rows
    tile_size = (width // cols - 3, height // rows - 1)

    tiles = []
    tile_id = 0
    for y in range(begin_position[0], height - 20, tile_size[1]):
        for x in range(begin_position[1], width - 20, tile_size[0]):
            position = (x + delta[0], y + delta[1], x + delta[2], y + delta[3])
            tiles.append(Tile(position=position, tile_id=tile_id))
            tile_id += 1
    return tiles


def capture(window_title: str, crop_percent: float, rows: int, cols: int) -> tuple:
    """Returns (board_image_path, tiles)."""
    image_path = screenshot_board(window_title, crop_percent)
    tiles = compute_tile_positions(image_path, rows, cols)
    return image_path, tiles
