"""
Chapter 2: An Array of Sequences — Examples
============================================
Original implementations demonstrating Python's sequence ecosystem.

Topics:
1. List comprehensions vs generator expressions — performance & semantics
2. Sequence taxonomy — container vs flat sequences
3. Slicing — advanced usage, slice objects, __setitem__ with slices
4. Augmented assignment — identity vs rebinding
5. array.array — typed flat sequences
6. memoryview — zero-copy binary data manipulation
7. deque — efficient double-ended queue
8. Sequence sorting — sorted() vs list.sort(), key functions

Run with: python examples.py
"""

from __future__ import annotations

import array
import sys
from collections import deque
from typing import Iterator


# =============================================================================
# PART 1: List Comprehensions vs Generator Expressions
# =============================================================================

def listcomp_vs_genexpr_demo() -> None:
    """
    List comprehensions build the full result in memory.
    Generator expressions yield items one at a time — lazy evaluation.

    KEY INSIGHT: Genexps are not "lazy listcomps" — they're fundamentally
    different objects with different protocols.
    """
    print("=== Part 1: Listcomp vs Genexpr ===\n")

    # ── List comprehension: builds all at once ──
    squares_list = [x ** 2 for x in range(10)]
    print(f"Listcomp result: {squares_list}")
    print(f"Type: {type(squares_list)}")
    print(f"Memory: ~{sys.getsizeof(squares_list)} bytes\n")

    # ── Generator expression: lazy ──
    squares_gen = (x ** 2 for x in range(10))
    print(f"Genexpr object: {squares_gen}")
    print(f"Type: {type(squares_gen)}")
    print(f"Memory: ~{sys.getsizeof(squares_gen)} bytes (always small!)\n")

    # Consuming the generator:
    print(f"list(genexpr): {list(squares_gen)}")
    # Generators are exhausted after one pass — this returns empty:
    print(f"list(genexpr) again: {list(squares_gen)}  ← exhausted!\n")

    # ── When to use genexpr: passing to a function ──
    total = sum(x ** 2 for x in range(1000))  # No intermediate list!
    print(f"sum of squares (genexpr): {total}")

    # Genexpr inside function call — parentheses not needed when it's the ONLY argument
    # sum(x**2 for x in range(1000))  — valid Python

    # ── Cartesian product: listcomp vs nested for ──
    # Readable alternative to nested loops:
    suits = ["♠", "♥", "♦", "♣"]
    ranks = ["A", "K", "Q"]
    cards = [(rank, suit) for suit in suits for rank in ranks]
    print(f"\nCartesian product ({len(cards)} cards):")
    print(f"  First 6: {cards[:6]}")

    # IMPORTANT: filter inside listcomp vs conditional expression
    # Filter (removes items):
    evens = [x for x in range(20) if x % 2 == 0]
    # Conditional expression (replaces items):
    abs_vals = [x if x >= 0 else -x for x in range(-5, 6)]
    print(f"Filtered evens: {evens}")
    print(f"Abs values via ternary: {abs_vals}")


# =============================================================================
# PART 2: Tuple Unpacking and Named Tuples
# =============================================================================

def tuple_unpacking_demo() -> None:
    """
    Tuples support elegant unpacking syntax.
    The * operator for grabbing variable-length portions.
    """
    print("\n=== Part 2: Tuple Unpacking ===\n")

    # Basic unpacking
    city_data = ("Tokyo", "JP", 36.933, (35.689722, 139.691667))
    name, country, pop, (lat, lon) = city_data  # nested unpacking!
    print(f"City: {name}, {country}")
    print(f"Population: {pop}M")
    print(f"Coordinates: lat={lat:.4f}, lon={lon:.4f}\n")

    # ── Star unpacking (*) — captures remainder ──
    first, *rest = [1, 2, 3, 4, 5]
    *beginning, last = [1, 2, 3, 4, 5]
    first2, *middle, last2 = [1, 2, 3, 4, 5]

    print(f"first, *rest = {first}, {rest}")
    print(f"*beginning, last = {beginning}, {last}")
    print(f"first, *middle, last = {first2}, {middle}, {last2}\n")

    # ── Swap without temporary variable ──
    a, b = 10, 20
    print(f"Before swap: a={a}, b={b}")
    a, b = b, a  # Python evaluates RHS fully before assignment
    print(f"After swap: a={a}, b={b}\n")

    # ── Unpacking in for loops ──
    cities = [("NYC", "US"), ("London", "UK"), ("Tokyo", "JP")]
    for city, country in cities:  # implicit unpacking
        print(f"  {city} ({country})")


# =============================================================================
# PART 3: Slicing Deep Dive
# =============================================================================

def slicing_demo() -> None:
    """
    Slicing is more powerful than [start:stop:step].
    Slice objects are first-class. Slice assignment modifies in place.
    """
    print("\n=== Part 3: Slicing Deep Dive ===\n")

    data = list(range(20))

    # ── Basic slicing ──
    print(f"data[1:5]     = {data[1:5]}")
    print(f"data[::2]     = {data[::2]}")   # every 2nd
    print(f"data[::-1]    = {data[::-1]}")  # reversed
    print(f"data[-3:]     = {data[-3:]}")   # last 3\n")

    # ── Named slices — making code self-documenting ──
    # Instead of: record[0:3], record[3:7], record[7:12]
    # Do this:
    NAME = slice(0, 3)
    DEPT = slice(3, 7)
    SALARY = slice(7, 12)

    record = "JohnEng  85000"
    print(f"Name: {record[NAME]!r}")
    print(f"Dept: {record[DEPT]!r}")
    print(f"Salary: {record[SALARY]!r}\n")

    # ── Slice assignment — modifies list in place ──
    mutable = list(range(10))
    print(f"Before: {mutable}")
    mutable[2:5] = [20, 30]  # Replace 3 elements with 2
    print(f"After mutable[2:5] = [20, 30]: {mutable}")
    mutable[::2] = [0] * (len(mutable) // 2 + len(mutable) % 2)
    print(f"After mutable[::2] = 0s: {mutable}\n")

    # ── Slice objects — first-class values ──
    s = slice(1, 10, 2)
    print(f"Slice object: {s}")
    print(f"Indices for length 15: {s.indices(15)}")  # normalizes to (1, 10, 2)
    print(f"Indices for length 5: {s.indices(5)}")    # clamps: (1, 5, 2)


# =============================================================================
# PART 4: Augmented Assignment and Identity
# =============================================================================

def augmented_assignment_demo() -> None:
    """
    += and *= behave differently for mutable vs immutable types.
    This is one of Python's most subtle behavioral differences.
    """
    print("\n=== Part 4: Augmented Assignment ===\n")

    # ── Mutable: += calls __iadd__, modifies in place ──
    lst = [1, 2, 3]
    original_id = id(lst)
    lst += [4, 5]  # Calls lst.__iadd__([4, 5]) → modifies in place
    print(f"List += : {lst}, id changed: {id(lst) != original_id}")  # False — same object!

    # ── Immutable: += creates a new object ──
    t = (1, 2, 3)
    original_id = id(t)
    t += (4, 5)  # Creates NEW tuple — can't modify tuples in place
    print(f"Tuple += : {t}, id changed: {id(t) != original_id}")  # True — new object!

    # ── The infamous tuple += bug ──
    # What does this do?
    weird_tuple = ([1, 2], [3, 4])
    try:
        weird_tuple[0] += [5, 6]
    except TypeError as e:
        print(f"\nweird_tuple[0] += [5, 6] → TypeError: {e}")
        print(f"But weird_tuple is now: {weird_tuple}")  # ← Modified despite error!

    print("""
LESSON: weird_tuple[0] += [5,6] does this:
  1. temp = weird_tuple[0].__iadd__([5,6])  → modifies the list in place (works!)
  2. weird_tuple[0] = temp                  → fails! tuples are immutable → TypeError
  3. The list is already modified from step 1
  
This is documented CPython behavior. The lesson: never put mutable objects
in tuples if you need to reassign them via augmented assignment.
""")


# =============================================================================
# PART 5: array.array — Memory-Efficient Flat Sequences
# =============================================================================

def array_demo() -> None:
    """
    array.array stores C values directly — no Python object per element.
    Use it for large sequences of a single numeric type.
    """
    print("=== Part 5: array.array ===\n")

    # Type codes: 'b'=signed byte, 'h'=short, 'i'=int, 'f'=float, 'd'=double
    floats = array.array("d", [1.5, 2.5, 3.5, 4.5, 5.5])
    print(f"array: {floats}")
    print(f"Type code: {floats.typecode}")
    print(f"Item size: {floats.itemsize} bytes per element")
    print(f"Total size: {sys.getsizeof(floats)} bytes\n")

    # Compare with list:
    float_list = [1.5, 2.5, 3.5, 4.5, 5.5]
    list_mem = sys.getsizeof(float_list) + sum(sys.getsizeof(x) for x in float_list)
    print(f"Equivalent list memory: {list_mem} bytes")
    print(f"array.array memory: {sys.getsizeof(floats)} bytes")
    print(f"Ratio: {list_mem / sys.getsizeof(floats):.1f}x more memory for list\n")

    # Saving and loading — array supports efficient I/O
    # arr.tofile(f) / arr.fromfile(f) — much faster than pickle for numeric data


# =============================================================================
# PART 6: memoryview — Zero-Copy Binary Operations
# =============================================================================

def memoryview_demo() -> None:
    """
    memoryview lets you inspect and modify binary data without copying.
    Critical for performance when working with large buffers.
    """
    print("\n=== Part 6: memoryview ===\n")

    # ── Basic memoryview on bytearray ──
    data = bytearray(b"Hello, Python!")
    mv = memoryview(data)

    print(f"Original: {bytes(data)}")
    print(f"memoryview[7:13]: {bytes(mv[7:13])}")

    # Modify without copying — directly edits `data`:
    mv[7:13] = b"World!"
    print(f"After mv[7:13] = b'World!': {bytes(data)}\n")

    # ── Reinterpreting memory layout ──
    # The same bytes can be viewed as different C types:
    nums = array.array("h", range(6))  # 6 signed shorts (2 bytes each = 12 bytes)
    mv = memoryview(nums)

    print(f"As shorts: {list(mv.tolist())}")
    mv_bytes = mv.cast("B")  # Reinterpret same bytes as unsigned chars
    print(f"Same bytes as unsigned chars: {list(mv_bytes.tolist())}")

    # ── Why memoryview matters: zero-copy slicing ──
    # Regular bytearray slicing: creates a copy
    big_data = bytearray(b"A" * 10_000_000)  # 10 MB

    # This creates a COPY of 1 MB:
    # chunk = big_data[0:1_000_000]

    # This creates a VIEW with no copy:
    mv_big = memoryview(big_data)
    chunk = mv_big[0:1_000_000]  # Zero bytes copied!
    print(f"\nZero-copy slice from 10MB buffer: {chunk.nbytes:,} bytes, no copy made")


# =============================================================================
# PART 7: deque — Efficient Double-Ended Queue
# =============================================================================

def deque_demo() -> None:
    """
    deque (double-ended queue) provides O(1) append and pop from BOTH ends.
    Use it when you need a queue/stack, not random access.
    """
    print("\n=== Part 7: deque ===\n")

    dq: deque[int] = deque([1, 2, 3, 4, 5], maxlen=5)
    print(f"deque: {dq}, maxlen={dq.maxlen}")

    # O(1) operations at both ends:
    dq.appendleft(0)  # Pushes out rightmost element (maxlen=5)
    print(f"After appendleft(0): {dq}  ← 5 was pushed out!")

    dq.append(99)  # Pushes out leftmost element
    print(f"After append(99): {dq}  ← 0 was pushed out!\n")

    # Rotation — O(n) but useful:
    dq2: deque[int] = deque(range(10))
    dq2.rotate(3)   # Move last 3 to front
    print(f"rotate(3): {dq2}")
    dq2.rotate(-3)  # Undo
    print(f"rotate(-3): {dq2}\n")

    # ── deque as a sliding window ──
    def sliding_max(data: list[int], window: int) -> list[int]:
        """Return max of each sliding window — deque keeps track of candidates."""
        result = []
        window_dq: deque[int] = deque()  # stores indices

        for i, val in enumerate(data):
            # Remove expired indices (left side of window)
            while window_dq and window_dq[0] < i - window + 1:
                window_dq.popleft()
            # Remove indices with smaller values from the right
            while window_dq and data[window_dq[-1]] < val:
                window_dq.pop()
            window_dq.append(i)
            if i >= window - 1:
                result.append(data[window_dq[0]])
        return result

    data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
    print(f"Data: {data}")
    print(f"Sliding max (window=3): {sliding_max(data, 3)}")


# =============================================================================
# PART 8: Sorting — sorted() vs list.sort()
# =============================================================================

def sorting_demo() -> None:
    """
    sorted() returns a new list. list.sort() modifies in place.
    Both use Timsort — O(n log n) worst case, O(n) for nearly-sorted data.
    """
    print("\n=== Part 8: Sorting ===\n")

    fruits = ["banana", "apple", "cherry", "date", "elderberry"]

    # sorted() — returns new list, works on any iterable
    sorted_fruits = sorted(fruits)
    print(f"sorted(): {sorted_fruits}")
    print(f"Original unchanged: {fruits}")

    # list.sort() — in place, returns None
    fruits.sort()
    print(f"After .sort(): {fruits}")

    # ── Custom sort keys ──
    words = ["banana", "apple", "fig", "cherry", "kiwi"]
    # Sort by length, then alphabetically:
    words_by_len = sorted(words, key=lambda w: (len(w), w))
    print(f"\nBy length then alpha: {words_by_len}")

    # ── Reverse ──
    desc = sorted(range(10), reverse=True)
    print(f"Descending: {desc}")

    # ── Stability: equal elements maintain relative order ──
    data2 = [(1, "b"), (2, "a"), (1, "a"), (2, "b")]
    # Sort only by first element — second element order preserved for ties:
    by_first = sorted(data2, key=lambda x: x[0])
    print(f"\nStable sort by first: {by_first}")
    # (1, 'b') before (1, 'a') because that was their original order


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    listcomp_vs_genexpr_demo()
    tuple_unpacking_demo()
    slicing_demo()
    augmented_assignment_demo()
    array_demo()
    memoryview_demo()
    deque_demo()
    sorting_demo()
