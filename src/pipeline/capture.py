"""Step 1: find the game window, screenshot its board, and slice it into Tiles."""

import os
from dataclasses import dataclass

import pyautogui
import pygetwindow as gw
from PIL import Image, ImageOps


@dataclass
class Tile:
    image: Image.Image
    position: tuple  # (x1, y1, x2, y2) pixel bbox within the captured screenshot
    tile_id: int
    name: str = "tile_picture"

    def save_image(self, folder_path: str) -> None:
        os.makedirs(folder_path, exist_ok=True)
        self.image.save(os.path.join(folder_path, f"{self.name}.png"), format="PNG")


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


def split_into_tiles(
    image_path: str,
    rows: int,
    cols: int,
    begin_position=(15, 15),
    delta=(10, 10, 40, 40),
    save_dir: str | None = None,
) -> list[Tile]:
    image = Image.open(image_path)
    width, height = image.size
    height = height // (rows + 1) * rows
    tile_size = (width // cols - 3, height // rows - 1)

    tiles = []
    tile_id = 0
    for y in range(begin_position[0], height - 20, tile_size[1]):
        for x in range(begin_position[1], width - 20, tile_size[0]):
            cell = image.crop((x, y, x + tile_size[0], y + tile_size[1]))
            cell = cell.crop(delta)
            cell = ImageOps.invert(cell)
            tile = Tile(
                image=cell,
                position=(x + delta[0], y + delta[1], x + delta[2], y + delta[3]),
                tile_id=tile_id,
                name="tile_picture{:03d}".format(tile_id),
            )
            if save_dir:
                tile.save_image(save_dir)
            tiles.append(tile)
            tile_id += 1
    return tiles


def capture(window_title: str, crop_percent: float, rows: int, cols: int, save_dir: str | None = None) -> list[Tile]:
    image_path = screenshot_board(window_title, crop_percent)
    return split_into_tiles(image_path, rows, cols, save_dir=save_dir)
