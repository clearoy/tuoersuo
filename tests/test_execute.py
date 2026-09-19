import pytest

pytest.importorskip("Quartz")
pytest.importorskip("pyautogui")

from PIL import Image, ImageDraw

from src.pipeline import capture, execute

GREEN = (60, 120, 90)
WHITE = (250, 250, 245)
ROWS, COLS = 2, 3


def make_tiles(tmp_path):
    path = tmp_path / "board.png"
    Image.new("RGB", (330, 240), GREEN).save(path)
    return capture.compute_tile_positions(str(path), ROWS, COLS, (15, 15), (15, 15))


def draw_board(tiles, present_cells):
    image = Image.new("RGB", (330, 240), GREEN)
    draw = ImageDraw.Draw(image)
    for row, col in present_cells:
        x1, y1, x2, y2 = tiles[(row - 1) * COLS + (col - 1)].position
        cx, cy, w, h = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
        draw.rectangle([cx - 0.38 * w, cy - 0.38 * h, cx + 0.38 * w, cy + 0.38 * h], fill=WHITE)
        draw.rectangle([cx - 0.1 * w, cy - 0.2 * h, cx + 0.1 * w, cy + 0.2 * h], fill=(0, 0, 0))  # the digit
    return image


def test_tile_with_digit_counts_as_present(tmp_path):
    tiles = make_tiles(tmp_path)
    image = draw_board(tiles, [(1, 1)])
    assert execute.is_tile_present(image, tiles[0])


def test_cleared_tile_counts_as_absent(tmp_path):
    tiles = make_tiles(tmp_path)
    image = draw_board(tiles, [(1, 2)])  # (1, 1) not drawn: bare green board
    assert not execute.is_tile_present(image, tiles[0])


def test_wait_until_cleared_sees_tiles_disappear(tmp_path, monkeypatch):
    tiles = make_tiles(tmp_path)
    frames = [draw_board(tiles, [(1, 1), (1, 2)]), draw_board(tiles, [])]
    monkeypatch.setattr(execute.capture, "grab_board", lambda *_a: (frames.pop(0), None))

    assert execute.wait_until_cleared("Game", 0.85, tiles, COLS, [(1, 1), (1, 2)], timeout=1.0, poll=0)


def test_wait_until_cleared_times_out_if_tiles_stay(tmp_path, monkeypatch):
    tiles = make_tiles(tmp_path)
    still_there = draw_board(tiles, [(1, 1)])
    monkeypatch.setattr(execute.capture, "grab_board", lambda *_a: (still_there, None))

    assert not execute.wait_until_cleared("Game", 0.85, tiles, COLS, [(1, 1)], timeout=0.05, poll=0.01)
