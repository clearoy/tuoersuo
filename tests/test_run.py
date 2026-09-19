import pytest

pytest.importorskip("Quartz")
pytest.importorskip("pyautogui")

from src import run
from src.config import Config
from src.pipeline.solve import Board, Move


def setup(monkeypatch, cleared_results):
    """Fake the mouse and the screen check; `cleared_results` is what each check returns."""
    drags = []
    monkeypatch.setattr(run.execute, "execute_move", lambda *a, **kw: drags.append(kw["drag_duration"]))
    results = list(cleared_results)
    monkeypatch.setattr(run.execute, "wait_until_cleared", lambda *a, **kw: results.pop(0))
    monkeypatch.setattr(run.execute, "save_failure_image", lambda *a, **kw: "failed_move.png")
    return drags


def test_move_that_clears_first_time_is_not_retried(monkeypatch):
    drags = setup(monkeypatch, [True])
    board = Board.from_digits([4, 6], 1, 2)
    assert run._play_move(board, [], None, Config(), Move((1, 1, 1, 2))) == 1
    assert len(drags) == 1


def test_move_that_clears_nothing_is_retried_more_slowly(monkeypatch):
    drags = setup(monkeypatch, [False, True])
    board = Board.from_digits([4, 6], 1, 2)
    config = Config()

    assert run._play_move(board, [], None, config, Move((1, 1, 1, 2))) == 2
    assert drags[1] > drags[0]


def test_move_that_never_clears_raises_with_the_digits(monkeypatch):
    setup(monkeypatch, [False, False])
    board = Board.from_digits([4, 6], 1, 2)

    with pytest.raises(RuntimeError, match=r"(?s)cleared nothing.*\[4, 6\]"):
        run._play_move(board, [], None, Config(), Move((1, 1, 1, 2)))


def test_verification_can_be_turned_off(monkeypatch):
    drags = setup(monkeypatch, [])  # wait_until_cleared must not be called
    board = Board.from_digits([4, 6], 1, 2)
    config = Config(verify_moves=False)

    assert run._play_move(board, [], None, config, Move((1, 1, 1, 2))) == 1
    assert len(drags) == 1
