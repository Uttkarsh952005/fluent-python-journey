"""
Chapter 1: Benchmarks — Python Data Model Performance
======================================================
Measuring the actual cost of dunder method dispatch vs direct C calls.

Run with: python benchmarks.py

Benchmarks:
1. len() vs __len__() on built-in list
2. len() vs __len__() on user-defined class
3. __contains__ override vs default __getitem__ scan
4. repr() overhead for different implementations
5. __bool__ vs __len__ truthiness chain
"""

from __future__ import annotations

import timeit
from typing import Any


# ─────────────────────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────────────────────

SAMPLE_LIST = list(range(1000))
NUMBER = 1_000_000  # 1 million iterations per benchmark


class MinimalSequence:
    """User-defined class with __len__ and __getitem__."""

    def __init__(self, data: list[Any]) -> None:
        self._data = data

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, idx: int | slice) -> Any:
        return self._data[idx]


class WithContains:
    """Has explicit __contains__ (O(1) set lookup)."""

    def __init__(self, data: list[int]) -> None:
        self._data = data
        self._set = set(data)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, idx: int) -> int:
        return self._data[idx]

    def __contains__(self, item: object) -> bool:
        return item in self._set  # O(1)


class WithoutContains:
    """No __contains__ — Python falls back to sequential __getitem__ scan."""

    def __init__(self, data: list[int]) -> None:
        self._data = data

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, idx: int) -> int:
        return self._data[idx]


class WithBool:
    """Explicit __bool__ method."""

    def __init__(self, value: bool) -> None:
        self._value = value

    def __bool__(self) -> bool:
        return self._value


class WithLenOnly:
    """No __bool__ — Python uses __len__ for truthiness."""

    def __init__(self, size: int) -> None:
        self._size = size

    def __len__(self) -> int:
        return self._size


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark Runner
# ─────────────────────────────────────────────────────────────────────────────


def run_benchmark(label: str, stmt: str, setup: str = "", number: int = NUMBER) -> float:
    """Run a timeit benchmark and return nanoseconds per operation."""
    elapsed = timeit.timeit(stmt=stmt, setup=setup, number=number, globals=globals())
    ns_per_op = (elapsed / number) * 1e9
    print(f"  {label:<50} {ns_per_op:>8.1f} ns/op")
    return ns_per_op


def section(title: str) -> None:
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark 1: len() vs .__len__() on built-in list
# ─────────────────────────────────────────────────────────────────────────────

section("Benchmark 1: len() vs .__len__() on built-in list")
print("  (Tests whether C-level shortcut in len() matters)")
print()

t1 = run_benchmark("len(SAMPLE_LIST)", "len(SAMPLE_LIST)")
t2 = run_benchmark("SAMPLE_LIST.__len__()", "SAMPLE_LIST.__len__()")

ratio = t2 / t1
print(f"\n  → __len__() is {ratio:.1f}x slower than len() on built-ins")
print("  Reason: len() uses C tp_as_sequence->sq_length; .__len__() goes through")
print("  Python's attribute lookup machinery (LOAD_ATTR + CALL opcodes).")


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark 2: len() vs .__len__() on user-defined class
# ─────────────────────────────────────────────────────────────────────────────

section("Benchmark 2: len() vs .__len__() on user-defined class")
print("  (For user classes, both must go through Python dispatch)")
print()

seq = MinimalSequence(SAMPLE_LIST)

t3 = run_benchmark("len(seq)", "len(seq)", setup="seq = MinimalSequence(SAMPLE_LIST)")
t4 = run_benchmark("seq.__len__()", "seq.__len__()", setup="seq = MinimalSequence(SAMPLE_LIST)")

ratio2 = t4 / t3
print(f"\n  → __len__() is {ratio2:.2f}x {'slower' if ratio2 > 1 else 'faster'} than len() on user class")
print("  Reason: len() still has slight overhead for checking return value is int >= 0.")


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark 3: __contains__ override vs __getitem__ fallback scan
# ─────────────────────────────────────────────────────────────────────────────

section("Benchmark 3: __contains__ (O(1)) vs __getitem__ scan (O(n))")
print("  Looking for item 999 (near end of 1000-element collection)")
print()

wc = WithContains(SAMPLE_LIST)
woc = WithoutContains(SAMPLE_LIST)

t5 = run_benchmark("999 in WithContains (O(1) set)", "999 in wc", setup="wc = WithContains(SAMPLE_LIST)", number=100_000)
t6 = run_benchmark("999 in WithoutContains (O(n) scan)", "999 in woc", setup="woc = WithoutContains(SAMPLE_LIST)", number=100_000)

ratio3 = t6 / t5
print(f"\n  → __contains__ override is {ratio3:.0f}x faster for near-end lookup")
print("  Lesson: Always implement __contains__ when you can do better than O(n).")


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark 4: Truthiness — __bool__ vs __len__ fallback
# ─────────────────────────────────────────────────────────────────────────────

section("Benchmark 4: Truthiness — __bool__ vs __len__ fallback")
print("  (Does adding __bool__ actually matter for performance?)")
print()

wb = WithBool(True)
wl = WithLenOnly(1)

t7 = run_benchmark("bool(WithBool)  — explicit __bool__", "bool(wb)", setup="wb = WithBool(True)")
t8 = run_benchmark("bool(WithLenOnly) — __len__ fallback", "bool(wl)", setup="wl = WithLenOnly(1)")

ratio4 = t8 / t7
print(f"\n  → __len__ fallback for truthiness is {ratio4:.1f}x slower than explicit __bool__")
print("  Lesson: For performance-critical code, implement __bool__ explicitly")
print("  rather than relying on the fallback chain.")


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

section("Summary — Key Takeaways")
print("""
  1. Use len() (the function), not obj.__len__() — it has a C shortcut for built-ins
  2. Always implement __contains__ for O(1) membership when possible
  3. Define __bool__ explicitly if truthiness matters for performance
  4. On user classes, len() and .__len__() have similar performance (no C shortcut)
  5. The performance gap matters most in tight loops with millions of iterations
""")
