"""Finds the game window and grabs a screenshot of its board area."""

import pygetwindow as gw
import pyautogui
from PIL import Image


class WindowCapture:
    def __init__(self, window_title: str, crop_percent: float = 0.85):
        self.window_title = window_title
        self.crop_percent = crop_percent

    def get_window(self):
        windows = gw.getWindowsWithTitle(self.window_title)
        if not windows:
            raise RuntimeError(f"No window found with title '{self.window_title}'")
        return windows[0]

    def capture(self, image_path: str = "screenshot.png") -> str:
        window = self.get_window()
        screenshot = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        screenshot.save(image_path, "PNG")
        self._crop_bottom(image_path, self.crop_percent)
        return image_path

    @staticmethod
    def _crop_bottom(image_path: str, percent_to_keep: float) -> None:
        image = Image.open(image_path)
        width, height = image.size
        kept_height = int(height * percent_to_keep)
        cropped = image.crop((0, height - kept_height, width, height))
        cropped.save(image_path)
