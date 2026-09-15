"""Translates a Move into real mouse input against the live game window."""

import pyautogui
import pygetwindow as gw

from src.solver import Move
from src.tile import Tile


class GameController:
    def __init__(self, window_title: str, drag_duration: float = 0.25):
        self.window_title = window_title
        self.drag_duration = drag_duration

    def _window_offset(self) -> tuple:
        windows = gw.getWindowsWithTitle(self.window_title)
        if not windows:
            raise RuntimeError(f"No window found with title '{self.window_title}'")
        window = windows[0]
        return window.left, window.top + 130

    def execute_move(self, tiles: list[Tile], move: Move, cols: int) -> None:
        x1, y1, x2, y2 = move.rect
        tile_a = tiles[(x1 - 1) * cols + (y1 - 1)]
        tile_b = tiles[(x2 - 1) * cols + (y2 - 1)]

        offset_x, offset_y = self._window_offset()
        start_x, start_y = self._tile_center(tile_a, offset_x, offset_y)
        end_x, end_y = self._tile_center(tile_b, offset_x, offset_y)

        pyautogui.click(start_x, start_y, button="left")
        pyautogui.dragTo(end_x, end_y, duration=self.drag_duration, button="left")

    @staticmethod
    def _tile_center(tile: Tile, offset_x: int, offset_y: int) -> tuple:
        cx = (tile.position[0] + tile.position[2]) // 2
        cy = (tile.position[1] + tile.position[3]) // 2
        return offset_x + cx, offset_y + cy + 15
