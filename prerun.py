"""Run before main.py: captures the game window, measures where the board actually sits
inside the screenshot (by pixel color), and saves the result to calibration.json, which
src/config.py loads automatically. Re-run whenever the window size or position changes.
"""

import json

from PIL import Image

from src.config import CALIBRATION_PATH, DEFAULT_CONFIG
from src.pipeline import capture


MIN_BOARD_PIXELS = 300  # a 16x10 board can't be smaller than this in a screenshot


def _is_board_pixel(rgb: tuple) -> bool:
    r, g, b = rgb[:3]
    if r > 200 and g > 200 and b > 200:  # white tile
        return True
    if g > r + 15 and g > b + 10 and g < 180:  # green board background
        return True
    return False


def detect_bounds(image_path: str, sample_step: int = 3, threshold: float = 0.3) -> tuple:
    """Returns (top, left, bottom_margin, right_margin) of the board in pixels."""
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    pixels = image.load()

    def row_is_board(y: int) -> bool:
        xs = range(0, width, sample_step)
        return sum(1 for x in xs if _is_board_pixel(pixels[x, y])) / len(xs) > threshold

    def col_is_board(x: int) -> bool:
        ys = range(0, height, sample_step)
        return sum(1 for y in ys if _is_board_pixel(pixels[x, y])) / len(ys) > threshold

    try:
        top = next(y for y in range(height) if row_is_board(y))
        bottom = next(y for y in range(height - 1, -1, -1) if row_is_board(y))
        left = next(x for x in range(width) if col_is_board(x))
        right = next(x for x in range(width - 1, -1, -1) if col_is_board(x))
    except StopIteration:
        raise RuntimeError("Could not find the board in the screenshot - is the game visible?")

    return top, left, height - 1 - bottom, width - 1 - right


if __name__ == "__main__":
    config = DEFAULT_CONFIG
    image_path, _tiles, geometry = capture.capture(
        config.window_title,
        config.capture_crop_percent,
        config.rows,
        config.cols,
    )
    width, height = Image.open(image_path).size
    if width < MIN_BOARD_PIXELS or height < MIN_BOARD_PIXELS:
        raise SystemExit(
            f"Captured image is only {width}x{height}px, too small to be the board - "
            f"open the game and keep it visible, then re-run. Nothing was saved. (See {image_path}.)"
        )
    top, left, bottom_margin, right_margin = detect_bounds(image_path)

    calibration = {
        "board_begin_position": [top, left],
        "board_end_margin": [bottom_margin, right_margin],
    }
    CALIBRATION_PATH.write_text(json.dumps(calibration, indent=2) + "\n")

    print(f"window={config.window_title!r} scale={geometry.scale:.2f}px/pt image={Image.open(image_path).size}")
    print(f"board_begin_position={tuple(calibration['board_begin_position'])}")
    print(f"board_end_margin={tuple(calibration['board_end_margin'])}")
    print(f"saved to {CALIBRATION_PATH}")
