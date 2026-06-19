"""
Chapter 1: Exercises — Python Data Model
=========================================
Original exercises to deepen understanding of special methods.
Each exercise builds on concepts from the chapter with increasing complexity.

Work through each exercise, then check your understanding against the hints.
"""

from __future__ import annotations

import math
from typing import Any, Iterator


# =============================================================================
# Exercise 1: Implement a Matrix class
# =============================================================================
# Build a 2D matrix that supports:
# - Indexing: matrix[row][col]
# - Length: len(matrix) returns number of rows
# - repr and str (different formats)
# - Addition: matrix1 + matrix2
# - Scalar multiplication: matrix * 3 and 3 * matrix
# - Equality comparison
# - Truthiness: empty (0-row or 0-col) matrix is falsy
#
# HINT: A matrix[row] returns a Row object that itself supports [col] indexing.
# This is a common pattern: __getitem__ returning another object with __getitem__.

class Row:
    """A single row of a matrix — supports column indexing."""

    def __init__(self, data: list[float]) -> None:
        self._data = data

    def __getitem__(self, col: int) -> float:
        return self._data[col]

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"Row({self._data})"


class Matrix:
    """
    2D matrix with full data model support.

    Your task: complete the missing methods below.
    Methods marked with # TODO need implementation.
    """

    def __init__(self, data: list[list[float]]) -> None:
        if not data or not data[0]:
            self._rows: list[list[float]] = []
            self._ncols = 0
        else:
            ncols = len(data[0])
            if any(len(row) != ncols for row in data):
                raise ValueError("All rows must have equal length")
            self._rows = [list(row) for row in data]
            self._ncols = ncols

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self._rows), self._ncols)

    def __len__(self) -> int:
        """Return number of rows."""
        return len(self._rows)

    def __getitem__(self, idx: int) -> Row:
        """Return a Row object for the given row index."""
        return Row(self._rows[idx])

    def __repr__(self) -> str:
        return f"Matrix(shape={self.shape}, data={self._rows})"

    def __str__(self) -> str:
        """Human-readable grid format."""
        if not self._rows:
            return "Matrix(empty)"
        lines = [" ".join(f"{v:6.2f}" for v in row) for row in self._rows]
        return "\n".join(lines)

    def __bool__(self) -> bool:
        """TODO: Implement — empty matrix should be falsy."""
        # HINT: Check if rows list is empty or ncols is 0
        return bool(self._rows) and self._ncols > 0

    def __eq__(self, other: object) -> bool:
        """TODO: Implement equality check."""
        # HINT: Check type, then compare shapes and data
        if not isinstance(other, Matrix):
            return NotImplemented
        return self._rows == other._rows

    def __add__(self, other: Matrix) -> Matrix:
        """TODO: Implement matrix addition."""
        # HINT: Check shapes match, then add element-wise
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.shape != other.shape:
            raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
        result = [
            [self._rows[i][j] + other._rows[i][j] for j in range(self._ncols)]
            for i in range(len(self._rows))
        ]
        return Matrix(result)

    def __mul__(self, scalar: float) -> Matrix:
        """TODO: Implement scalar multiplication."""
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        result = [[v * scalar for v in row] for row in self._rows]
        return Matrix(result)

    def __rmul__(self, scalar: float) -> Matrix:
        """Enables 3 * matrix."""
        return self.__mul__(scalar)


# =============================================================================
# Exercise 2: Implement a TimeStamp class
# =============================================================================
# Build a TimeStamp class representing duration in seconds that supports:
# - abs(ts) returns total seconds (always positive)
# - ts1 + ts2 adds durations
# - ts * n scales duration
# - repr shows "TimeStamp(Xh Ym Zs)"
# - bool(ts) is False for zero duration
# - Comparison operators: <, >, ==

class TimeStamp:
    """Duration represented as total seconds, with rich dunder support."""

    def __init__(self, total_seconds: float) -> None:
        self._total = float(total_seconds)

    @classmethod
    def from_hms(cls, hours: int = 0, minutes: int = 0, seconds: float = 0) -> TimeStamp:
        """Factory: TimeStamp.from_hms(1, 30, 0) → 90 minutes."""
        return cls(hours * 3600 + minutes * 60 + seconds)

    @property
    def hours(self) -> int:
        return int(self._total) // 3600

    @property
    def minutes(self) -> int:
        return (int(self._total) % 3600) // 60

    @property
    def seconds(self) -> float:
        return self._total % 60

    def __abs__(self) -> float:
        """Return total seconds as a positive float."""
        return abs(self._total)

    def __bool__(self) -> bool:
        """Zero duration is falsy."""
        return self._total != 0.0

    def __repr__(self) -> str:
        return f"TimeStamp({self.hours}h {self.minutes}m {self.seconds:.1f}s)"

    def __add__(self, other: TimeStamp) -> TimeStamp:
        if not isinstance(other, TimeStamp):
            return NotImplemented
        return TimeStamp(self._total + other._total)

    def __mul__(self, factor: float) -> TimeStamp:
        if not isinstance(factor, (int, float)):
            return NotImplemented
        return TimeStamp(self._total * factor)

    def __rmul__(self, factor: float) -> TimeStamp:
        return self.__mul__(factor)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TimeStamp):
            return math.isclose(self._total, other._total)
        return NotImplemented

    def __lt__(self, other: TimeStamp) -> bool:
        if not isinstance(other, TimeStamp):
            return NotImplemented
        return self._total < other._total

    def __le__(self, other: TimeStamp) -> bool:
        return self < other or self == other


# =============================================================================
# Exercise 3: Iterable Temperature Sensor Log
# =============================================================================
# A sensor log that:
# - Iterates over (timestamp, temperature) readings
# - len() gives total readings
# - bool() is False if no readings above threshold
# - repr shows summary statistics

class TempSensorLog:
    """
    Temperature sensor log with statistical summary.

    Demonstrates: __len__, __iter__, __bool__, __repr__, __getitem__
    """

    def __init__(self, readings: list[tuple[str, float]], threshold: float = 37.5) -> None:
        self._readings = readings
        self._threshold = threshold

    def __len__(self) -> int:
        return len(self._readings)

    def __iter__(self) -> Iterator[tuple[str, float]]:
        return iter(self._readings)

    def __getitem__(self, idx: int | slice) -> Any:
        return self._readings[idx]

    def __bool__(self) -> bool:
        """True if any reading exceeds the threshold — alerts are active."""
        return any(temp > self._threshold for _, temp in self._readings)

    def __repr__(self) -> str:
        if not self._readings:
            return "TempSensorLog(empty)"
        temps = [t for _, t in self._readings]
        return (
            f"TempSensorLog({len(self)} readings, "
            f"min={min(temps):.1f}, max={max(temps):.1f}, "
            f"avg={sum(temps)/len(temps):.1f}, "
            f"alerts={'YES' if bool(self) else 'NO'})"
        )


# =============================================================================
# Test / Demo
# =============================================================================

def run_exercises() -> None:
    print("=== Exercise 1: Matrix ===")
    m1 = Matrix([[1, 2, 3], [4, 5, 6]])
    m2 = Matrix([[7, 8, 9], [10, 11, 12]])
    print(f"m1:\n{m1}")
    print(f"m1[0][2] = {m1[0][2]}")
    print(f"m1 + m2:\n{m1 + m2}")
    print(f"m1 * 2:\n{m1 * 2}")
    print(f"3 * m1:\n{3 * m1}")
    print(f"bool(m1) = {bool(m1)}")
    print(f"bool(Matrix([])) = {bool(Matrix([]))}")

    print("\n=== Exercise 2: TimeStamp ===")
    t1 = TimeStamp.from_hms(1, 30, 0)
    t2 = TimeStamp.from_hms(0, 45, 30)
    print(f"t1 = {t1!r}")
    print(f"t2 = {t2!r}")
    print(f"t1 + t2 = {t1 + t2!r}")
    print(f"t1 * 2 = {t1 * 2!r}")
    print(f"abs(t1) = {abs(t1)}")
    print(f"t1 > t2: {t1 > t2}")  # type: ignore[operator]
    print(f"bool(TimeStamp(0)): {bool(TimeStamp(0))}")

    print("\n=== Exercise 3: TempSensorLog ===")
    log = TempSensorLog([
        ("09:00", 36.5),
        ("10:00", 37.0),
        ("11:00", 38.2),  # above threshold
        ("12:00", 36.8),
    ])
    print(f"log = {log!r}")
    print(f"bool(log) [has alerts?] = {bool(log)}")
    print(f"len(log) = {len(log)}")
    print(f"log[2] = {log[2]}")

    normal_log = TempSensorLog([("09:00", 36.5), ("10:00", 37.0)])
    print(f"normal_log alerts: {bool(normal_log)}")


if __name__ == "__main__":
    run_exercises()
