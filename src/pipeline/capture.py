"""Step 1: find the game window, screenshot its board, and compute each cell's pixel position.

No per-tile image cropping happens here: OCR (step 2) reads the whole board image in one
call, so this step only needs cell geometry, used later for click targeting in step 4.

Window lookup goes straight through Quartz - pygetwindow's macOS backend is an
unfinished stub (no getAllWindows/getWindowsWithTitle, Window methods raise
NotImplementedError) so it isn't usable here.
"""

from dataclasses import dataclass

import pyautogui
import Quartz
from PIL import Image


@dataclass
class Tile:
    position: tuple  # (x1, y1, x2, y2) pixel bbox within screenshot.png (the cropped image)
    tile_id: int


@dataclass
class CaptureGeometry:
    """Converts a Tile's pixel position (in the cropped screenshot image) into an
    absolute on-screen point coordinate, given the live window's current position.

    Two real, measured quantities replace what used to be hardcoded fudge constants:
    - crop_offset_y: exact pixels trimmed off the top of the raw screenshot by the crop.
    - scale: screenshot pixels per screen point. On a Retina display, pyautogui's
      screenshot is captured at 2x the resolution of the point-based coordinates that
      Quartz window bounds and pyautogui.click/dragTo use, so this must be divided out.
    """

    crop_offset_y: int
    scale: float

    def to_screen_point(self, window_left: int, window_top: int, x: float, y: float) -> tuple:
        full_image_y = y + self.crop_offset_y
        return window_left + x / self.scale, window_top + full_image_y / self.scale


def get_window_bounds(window_title: str) -> tuple:
    """Returns (left, top, width, height) of the first on-screen window whose owner
    name or window title contains window_title."""
    windows = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListExcludeDesktopElements | Quartz.kCGWindowListOptionOnScreenOnly,
        Quartz.kCGNullWindowID,
    )
    for window in windows:
        owner = window.get(Quartz.kCGWindowOwnerName, "") or ""
        name = window.get(Quartz.kCGWindowName, "") or ""
        if window_title in owner or window_title in name:
            bounds = window["kCGWindowBounds"]
            return int(bounds["X"]), int(bounds["Y"]), int(bounds["Width"]), int(bounds["Height"])
    raise RuntimeError(f"No window found with title '{window_title}'")


def screenshot_board(window_title: str, crop_percent: float, image_path: str = "screenshot.png") -> tuple:
    """Returns (image_path, CaptureGeometry)."""
    left, top, width, height = get_window_bounds(window_title)
    image = pyautogui.screenshot(region=(left, top, width, height))
    image.save(image_path, "PNG")

    scale = image.width / width  # screenshot pixels per screen point (2.0 on Retina)

    full_height = image.height
    kept_height = int(full_height * crop_percent)
    crop_offset_y = full_height - kept_height
    cropped = image.crop((0, crop_offset_y, image.width, full_height))
    cropped.save(image_path)

    return image_path, CaptureGeometry(crop_offset_y=crop_offset_y, scale=scale)


def compute_tile_positions(
    image_path: str,
    rows: int,
    cols: int,
    begin_position=(15, 15),
    end_margin=(15, 15),
) -> list[Tile]:
    """Loops over exactly `rows` x `cols` cells, dividing the board evenly with float
    math so every tile's center is the true grid-cell center - no per-tile fixed-pixel
    crop (the old `delta` sub-crop was tuned for a different window's tile size and only
    approximated the center for one specific resolution)."""
    width, height = Image.open(image_path).size

    cell_width = (width - begin_position[1] - end_margin[1]) / cols
    cell_height = (height - begin_position[0] - end_margin[0]) / rows

    tiles = []
    tile_id = 0
    for row in range(rows):
        y = begin_position[0] + row * cell_height
        for col in range(cols):
            x = begin_position[1] + col * cell_width
            position = (x, y, x + cell_width, y + cell_height)
            tiles.append(Tile(position=position, tile_id=tile_id))
            tile_id += 1
    return tiles


def capture(
    window_title: str,
    crop_percent: float,
    rows: int,
    cols: int,
    begin_position=(15, 15),
    end_margin=(15, 15),
) -> tuple:
    """Returns (board_image_path, tiles, CaptureGeometry)."""
    image_path, geometry = screenshot_board(window_title, crop_percent)
    tiles = compute_tile_positions(image_path, rows, cols, begin_position, end_margin)
    return image_path, tiles, geometry
