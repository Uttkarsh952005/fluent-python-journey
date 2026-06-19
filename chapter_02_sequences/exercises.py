"""
Chapter 2: Exercises — Sequences
=================================
Progressive exercises to build deep understanding of sequence types.
"""

from __future__ import annotations

import array
from collections import deque
from typing import Any, Iterator


# =============================================================================
# Exercise 1: Implement a Ring Buffer using deque
# =============================================================================
# Build a RingBuffer class that:
# - Has fixed capacity (maxlen)
# - Overwrites oldest data when full
# - Supports: append, __len__, __iter__, __getitem__, is_full, as_list
# - Reports utilization percentage

class RingBuffer:
    """Fixed-size ring buffer backed by a deque(maxlen=capacity)."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self._capacity = capacity
        self._data: deque[Any] = deque(maxlen=capacity)

    def append(self, item: Any) -> None:
        """Add item. If full, oldest item is automatically evicted."""
        self._data.append(item)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __getitem__(self, idx: int) -> Any:
        return self._data[idx]

    def __repr__(self) -> str:
        return f"RingBuffer(capacity={self._capacity}, size={len(self)}, data={list(self._data)})"

    @property
    def is_full(self) -> bool:
        return len(self._data) == self._capacity

    @property
    def utilization(self) -> float:
        return len(self._data) / self._capacity

    def as_list(self) -> list[Any]:
        return list(self._data)


# =============================================================================
# Exercise 2: Custom Slice-Aware CSV Reader
# =============================================================================
# Build a CSVData class that:
# - Stores parsed rows as a list of tuples
# - Supports slicing: data[0:10] returns first 10 rows
# - Supports named column access: data.column("name")
# - Supports filtering: data.where(lambda row: row[2] > 50)
# - Is sortable by column

class CSVData:
    """In-memory CSV table with slice and filter support."""

    def __init__(self, headers: list[str], rows: list[tuple[Any, ...]]) -> None:
        self._headers = headers
        self._rows = rows
        self._col_index = {name: i for i, name in enumerate(headers)}

    @classmethod
    def from_text(cls, text: str, delimiter: str = ",") -> CSVData:
        lines = text.strip().splitlines()
        headers = [h.strip() for h in lines[0].split(delimiter)]
        rows = [
            tuple(v.strip() for v in line.split(delimiter))
            for line in lines[1:]
        ]
        return cls(headers, rows)

    def __len__(self) -> int:
        return len(self._rows)

    def __getitem__(self, idx: int | slice) -> Any:
        result = self._rows[idx]
        if isinstance(idx, slice):
            return CSVData(self._headers, list(result))
        return result

    def __repr__(self) -> str:
        return f"CSVData({len(self)} rows, columns={self._headers})"

    def column(self, name: str) -> list[Any]:
        """Extract a single column by name."""
        idx = self._col_index[name]
        return [row[idx] for row in self._rows]

    def where(self, predicate: Any) -> CSVData:
        """Filter rows by a predicate function."""
        return CSVData(self._headers, [r for r in self._rows if predicate(r)])

    def sort_by(self, column: str, reverse: bool = False) -> CSVData:
        """Return a new CSVData sorted by the given column."""
        idx = self._col_index[column]
        sorted_rows = sorted(self._rows, key=lambda r: r[idx], reverse=reverse)
        return CSVData(self._headers, sorted_rows)

    def head(self, n: int = 5) -> CSVData:
        return self[0:n]


# =============================================================================
# Exercise 3: TypedList — A list that enforces element type
# =============================================================================
# Build a TypedList that:
# - Only accepts elements of a specific type
# - Supports all list operations (append, extend, __getitem__, __setitem__)
# - Raises TypeError for wrong types with a clear message

class TypedList:
    """
    A list that enforces a single element type.

    Example:
        tl = TypedList(float)
        tl.append(3.14)   # OK
        tl.append("hi")   # TypeError
    """

    def __init__(self, element_type: type, initial: list[Any] | None = None) -> None:
        self._type = element_type
        self._data: list[Any] = []
        if initial:
            for item in initial:
                self.append(item)

    def _check(self, value: Any) -> None:
        if not isinstance(value, self._type):
            raise TypeError(
                f"TypedList[{self._type.__name__}] cannot accept "
                f"{type(value).__name__!r}: {value!r}"
            )

    def append(self, item: Any) -> None:
        self._check(item)
        self._data.append(item)

    def extend(self, items: Any) -> None:
        checked = list(items)
        for item in checked:
            self._check(item)
        self._data.extend(checked)

    def __setitem__(self, idx: int, value: Any) -> None:
        self._check(value)
        self._data[idx] = value

    def __getitem__(self, idx: int | slice) -> Any:
        return self._data[idx]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __repr__(self) -> str:
        return f"TypedList[{self._type.__name__}]({self._data!r})"


# =============================================================================
# Exercise 4: Sliding Window with Statistics
# =============================================================================
# Build a StreamStats class that:
# - Accepts a stream of floats one at a time
# - Maintains a sliding window of last N values
# - Reports: mean, min, max, latest value
# - Uses deque(maxlen=N) — no other data structures

class StreamStats:
    """Real-time statistics over a sliding window of numeric values."""

    def __init__(self, window_size: int) -> None:
        self._window: deque[float] = deque(maxlen=window_size)

    def update(self, value: float) -> None:
        """Add a new value; oldest is evicted if window is full."""
        self._window.append(float(value))

    @property
    def mean(self) -> float | None:
        if not self._window:
            return None
        return sum(self._window) / len(self._window)

    @property
    def minimum(self) -> float | None:
        return min(self._window) if self._window else None

    @property
    def maximum(self) -> float | None:
        return max(self._window) if self._window else None

    @property
    def latest(self) -> float | None:
        return self._window[-1] if self._window else None

    def __repr__(self) -> str:
        return (
            f"StreamStats(n={len(self._window)}, "
            f"mean={self.mean:.2f}, "
            f"range=[{self.minimum:.2f}, {self.maximum:.2f}])"
            if self._window else "StreamStats(empty)"
        )


# =============================================================================
# Demo / Tests
# =============================================================================

def run_exercises() -> None:
    print("=== Exercise 1: RingBuffer ===")
    rb = RingBuffer(capacity=5)
    for i in range(8):  # More than capacity
        rb.append(i)
    print(f"After 8 appends into capacity-5 buffer: {rb}")
    print(f"  is_full: {rb.is_full}, utilization: {rb.utilization:.0%}")
    print(f"  as_list: {rb.as_list()}")

    print("\n=== Exercise 2: CSVData ===")
    csv_text = """name,dept,salary
Alice,Engineering,95000
Bob,Marketing,72000
Charlie,Engineering,110000
Diana,HR,68000
Eve,Engineering,88000"""

    data = CSVData.from_text(csv_text)
    print(f"data: {data}")
    print(f"Engineering only: {data.where(lambda r: r[1] == 'Engineering')}")
    print(f"Salaries: {data.column('salary')}")
    print(f"First 2 rows: {data.head(2)}")

    print("\n=== Exercise 3: TypedList ===")
    tl = TypedList(float, [1.0, 2.5, 3.14])
    tl.append(4.0)
    print(f"TypedList: {tl}")
    try:
        tl.append("not a float")
    except TypeError as e:
        print(f"Caught TypeError: {e}")

    print("\n=== Exercise 4: StreamStats ===")
    stats = StreamStats(window_size=5)
    values = [10, 12, 8, 15, 9, 11, 7, 14]
    for v in values:
        stats.update(v)
        print(f"  After {v}: {stats}")


if __name__ == "__main__":
    run_exercises()
