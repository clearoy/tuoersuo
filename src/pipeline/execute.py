"""Step 4: turn a Move into real mouse input against the live game window.

The mini-program board runs in a webview/canvas, which needs real mousemove/mousedown/
mouseup events spaced out in time to register a drag - teleporting the cursor and
firing click+drag back-to-back gets missed or misread. So this moves smoothly to the
start tile, pauses, clicks, drags slowly, then lets the game settle before returning.
"""

import time

import pyautogui

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
