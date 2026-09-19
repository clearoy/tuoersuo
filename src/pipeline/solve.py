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


def find_moves(grid: list, rows: int, cols: int) -> list:
    """Every move available on `grid` as (cell_count, area, rect), sorted smallest first.

    Only "tight" rectangles are returned (each edge touches at least one non-empty cell),
    so each distinct set of cells appears exactly once instead of once per empty margin.
    """
    moves = []
    for x1 in range(1, rows + 1):
        for y1 in range(1, cols + 1):
            col_sum = [0] * (cols + 1)
            col_count = [0] * (cols + 1)
            y_limit = cols  # columns past this already overshoot 10 for every taller rect
            for x2 in range(x1, rows + 1):
                row = grid[x2]
                for y in range(y1, y_limit + 1):
                    if row[y]:
                        col_sum[y] += row[y]
                        col_count[y] += 1
                total = 0
                count = 0
                for y2 in range(y1, y_limit + 1):
                    total += col_sum[y2]
                    count += col_count[y2]
                    if total > 10:
                        y_limit = y2 - 1
                        break
                    if (
                        total == 10
                        and col_count[y1]
                        and col_count[y2]
                        and any(grid[x1][y1 : y2 + 1])
                        and any(row[y1 : y2 + 1])
                    ):
                        moves.append((count, (x2 - x1 + 1) * (y2 - y1 + 1), (x1, y1, x2, y2)))
                if y_limit < y1:
                    break
    moves.sort()
    return moves


class SmallestFirstSolver(Solver):
    """Greedy, but always takes the move that clears the fewest cells (ties: smallest area)."""

    def next_move(self, board: Board) -> Optional[Move]:
        moves = find_moves(board.grid, board.rows, board.cols)
        return Move(moves[0][2]) if moves else None


def _grid_key(grid: list) -> tuple:
    return tuple(map(tuple, grid))


def _coverage(grid: list, moves: list) -> int:
    """How many non-empty cells are part of at least one available move."""
    covered = set()
    for _count, _area, (x1, y1, x2, y2) in moves:
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                if grid[i][j]:
                    covered.add((i, j))
    return len(covered)


class BeamSearchSolver(Solver):
    """Plans a whole game ahead with beam search, then plays the plan move by move.

    Each level expands every kept board with its `branching` smallest moves, then keeps
    the `beam_width` best children, ranked by cells cleared so far plus how many cells
    can still be cleared (coverage). Ranking by cells cleared alone favors big rectangles
    and scores worse than plain greedy; coverage rewards keeping options open. Identical
    boards reached by different move orders are merged. If the board ever differs from
    what the plan expects, or the plan runs out while moves remain, it re-plans.
    """

    def __init__(self, beam_width: int = 20, branching: int = 6):
        self.beam_width = beam_width
        self.branching = branching
        self._plan: list = []
        self._expected_key = None

    def next_move(self, board: Board) -> Optional[Move]:
        if not self._plan or _grid_key(board.grid) != self._expected_key:
            self._plan = self._search(board)
        if not self._plan:
            return None

        rect = self._plan.pop(0)
        after = [row[:] for row in board.grid]
        _clear(after, rect)
        self._expected_key = _grid_key(after)
        return Move(rect)

    def _search(self, board: Board) -> list:
        rows, cols = board.rows, board.cols
        start = [row[:] for row in board.grid]
        # node: (grid, cells cleared, rects so far, moves available on grid)
        beam = [(start, 0, (), find_moves(start, rows, cols))]
        best_cleared, best_path = 0, ()

        while beam:
            children = {}
            for grid, cleared, path, moves in beam:
                for count, _area, rect in moves[: self.branching]:
                    child = [row[:] for row in grid]
                    _clear(child, rect)
                    key = _grid_key(child)
                    if key not in children:
                        children[key] = (child, cleared + count, path + (rect,), find_moves(child, rows, cols))

            for _grid, cleared, path, _moves in children.values():
                if cleared > best_cleared:
                    best_cleared, best_path = cleared, path

            ranked = sorted(children.values(), key=lambda n: n[1] + _coverage(n[0], n[3]), reverse=True)
            beam = ranked[: self.beam_width]

        return list(best_path)


def _clear(grid: list, rect: tuple) -> None:
    x1, y1, x2, y2 = rect
    for i in range(x1, x2 + 1):
        for j in range(y1, y2 + 1):
            grid[i][j] = 0


SOLVER_NAMES = ("greedy", "smallest", "beam")


def make_solver(name: str, beam_width: int = 20, beam_branching: int = 6) -> Solver:
    if name == "greedy":
        return GreedySolver()
    if name == "smallest":
        return SmallestFirstSolver()
    if name == "beam":
        return BeamSearchSolver(beam_width, beam_branching)
    raise ValueError(f"Unknown solver {name!r}; choose one of {', '.join(SOLVER_NAMES)}")
