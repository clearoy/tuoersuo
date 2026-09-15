"""Step 4: turn a Move into real mouse input against the live game window."""

import pyautogui

from src.pipeline.capture import Tile, get_window
from src.pipeline.solve import Move


def _tile_center(tile: Tile, offset_x: int, offset_y: int) -> tuple:
    cx = (tile.position[0] + tile.position[2]) // 2
    cy = (tile.position[1] + tile.position[3]) // 2
    return offset_x + cx, offset_y + cy + 15


def execute_move(
    window_title: str,
    tiles: list[Tile],
    move: Move,
    cols: int,
    drag_duration: float = 0.25,
) -> None:
    x1, y1, x2, y2 = move.rect
    tile_a = tiles[(x1 - 1) * cols + (y1 - 1)]
    tile_b = tiles[(x2 - 1) * cols + (y2 - 1)]

    window = get_window(window_title)
    offset_x, offset_y = window.left, window.top + 130
    start_x, start_y = _tile_center(tile_a, offset_x, offset_y)
    end_x, end_y = _tile_center(tile_b, offset_x, offset_y)

    pyautogui.click(start_x, start_y, button="left")
    pyautogui.dragTo(end_x, end_y, duration=drag_duration, button="left")
