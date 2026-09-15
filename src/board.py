"""The digit grid: rectangle sum/count queries and clearing. 1-indexed, 0 = empty cell."""

from dataclasses import dataclass


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
