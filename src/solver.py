"""Move-finding strategies. Swap GreedySolver for an RL-backed Solver later - same interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from src.board import Board


@dataclass(frozen=True)
class Move:
    rect: tuple  # (x1, y1, x2, y2), inclusive, 1-indexed


class Solver(ABC):
    @abstractmethod
    def next_move(self, board: Board) -> Optional[Move]:
        """Return one valid move given the current board state, or None if no move remains."""


class GreedySolver(Solver):
    """Scans for any rectangle summing to 10, preferring fewer non-empty cells first.

    If a full board scan finds nothing at the current complexity threshold, the
    threshold is relaxed and the board is scanned again.
    """

    def __init__(self, initial_threshold: float = 2.0, threshold_step: float = 0.05, max_threshold: float = 20.0):
        self.threshold = initial_threshold
        self.threshold_step = threshold_step
        self.max_threshold = max_threshold

    def next_move(self, board: Board) -> Optional[Move]:
        while True:
            move = self._scan(board)
            if move is not None:
                return move
            if self.threshold >= self.max_threshold:
                return None
            self.threshold += self.threshold_step

    def _scan(self, board: Board) -> Optional[Move]:
        for x1 in range(1, board.rows + 1):
            for y1 in range(1, board.cols + 1):
                move = self._grow_rect(board, x1, y1)
                if move is not None:
                    return move
        return None

    def _grow_rect(self, board: Board, x1: int, y1: int) -> Optional[Move]:
        for x2 in range(x1, board.rows + 1):
            for y2 in range(y1, board.cols + 1):
                total, score = board.query((x1, y1, x2, y2))
                if total == 10 and score <= self.threshold:
                    return Move((x1, y1, x2, y2))
                if total > 10:
                    break
        return None
