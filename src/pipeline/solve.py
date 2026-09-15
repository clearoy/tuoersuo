"""Step 3: board state + move-finding strategies.

This is the only file you need to touch to try an RL model: implement Solver.next_move
and pass an instance into src.run.run(config, solver=YourSolver()).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class Board:
    rows: int
    cols: int
    grid: list

    @classmethod
    def from_digits(cls, digits: list, rows: int, cols: int) -> "Board":
        if len(digits) != rows * cols:
            raise ValueError(f"expected {rows * cols} digits, got {len(digits)}")
        grid = [[0] * (cols + 1) for _ in range(rows + 1)]
        for idx, digit in enumerate(digits):
            grid[idx // cols + 1][idx % cols + 1] = int(digit)
        return cls(rows, cols, grid)

    def query(self, rect: tuple) -> tuple:
        """Returns (sum, count_of_nonempty_cells) inside inclusive rect (x1, y1, x2, y2)."""
        x1, y1, x2, y2 = rect
        total = 0
        count = 0
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                value = self.grid[i][j]
                if value:
                    total += value
                    count += 1
        return total, count

    def clear(self, rect: tuple) -> None:
        x1, y1, x2, y2 = rect
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                self.grid[i][j] = 0

    def remaining_score(self) -> int:
        return sum(self.grid[i][j] for i in range(1, self.rows + 1) for j in range(1, self.cols + 1))

    def is_solved(self) -> bool:
        return self.remaining_score() == 0

    def show(self) -> None:
        for row in self.grid[1:]:
            print(row[1:])


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
