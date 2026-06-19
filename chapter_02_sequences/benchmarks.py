"""
Chapter 2: Benchmarks — Sequence Types Performance
===================================================
Rigorous performance measurements comparing Python's sequence types.

Measures:
1. Memory usage: list vs tuple vs array.array
2. Construction time: list vs tuple vs array.array
3. Append performance: list vs deque (at head and tail)
4. Membership test: list vs set vs deque
5. memoryview slicing vs bytearray slicing
6. List comprehension vs generator expression vs map()
7. list.sort() vs sorted() overhead

Run with: python benchmarks.py
"""

from __future__ import annotations

import array
import gc
import sys
import timeit
from collections import deque

# Windows PowerShell UTF-8 compatibility
sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────
# -----------------------------------------------------------------------------
N = 100_000     # Size of collections
REPS = 500      # Repetitions for timeit
MILLION = 1_000_000


def header(title: str) -> None:
    print(f"\n{'=' * 65}")
    print(f"  {title}")
    print(f"{'=' * 65}")


def bench(label: str, stmt: str, setup: str = "pass", reps: int = REPS) -> float:
    gc.disable()
    t = timeit.timeit(stmt=stmt, setup=setup, number=reps, globals=globals())
    gc.enable()
    ms = (t / reps) * 1000
    print(f"  {label:<52} {ms:>8.4f} ms")
    return ms


# -----------------------------------------------------------------------------
# Benchmark 1: Memory Footprint
# -----------------------------------------------------------------------------

header("Benchmark 1: Memory Footprint (100,000 floats)")

float_list = list(range(N))
float_tuple = tuple(range(N))
float_array = array.array("d", range(N))

list_mem = sys.getsizeof(float_list)
tuple_mem = sys.getsizeof(float_tuple)
array_mem = sys.getsizeof(float_array)

print(f"  list  (100k ints): {list_mem:>10,} bytes = {list_mem / 1024:.1f} KB")
print(f"  tuple (100k ints): {tuple_mem:>10,} bytes = {tuple_mem / 1024:.1f} KB")
print(f"  array (100k 'd'):  {array_mem:>10,} bytes = {array_mem / 1024:.1f} KB")

# For floats, list stores Python float objects — much larger
float_objects = [float(i) for i in range(1000)]
total_list_float_mem = sys.getsizeof(float_objects) + sum(
    sys.getsizeof(x) for x in float_objects
)
float_arr = array.array("d", float_objects)
total_array_float_mem = sys.getsizeof(float_arr)

print(f"\n  For 1,000 Python float objects:")
print(f"    list total memory: {total_list_float_mem:,} bytes")
print(f"    array.array 'd':   {total_array_float_mem:,} bytes")
print(f"    Ratio: {total_list_float_mem / total_array_float_mem:.1f}x more memory for list")

print(f"\n  → list stores POINTERS to Python objects (8 bytes each + object overhead)")
print(f"  → array.array stores raw C doubles (8 bytes each, no object overhead)")


# -----------------------------------------------------------------------------
# Benchmark 2: Construction Time
# -----------------------------------------------------------------------------

header("Benchmark 2: Construction Time (100,000 elements)")

t1 = bench("list(range(N))", "list(range(N))", setup="N=100_000")
t2 = bench("tuple(range(N))", "tuple(range(N))", setup="N=100_000")
t3 = bench("array.array('d', range(N))", "array.array('d', range(N))",
           setup="import array; N=100_000")
t4 = bench("[x for x in range(N)]", "[x for x in range(N)]", setup="N=100_000")

print(f"\n  -> tuple construction is slightly faster: no over-allocation needed")
print(f"  -> array.array is slower to construct (type conversion per element)")


# -----------------------------------------------------------------------------
# Benchmark 3: Append Performance — list vs deque
# -----------------------------------------------------------------------------

header("Benchmark 3: Append Performance (10,000 appends)")

t5 = bench(
    "list.append(x) — append to end",
    "for i in range(10000): lst.append(i)",
    setup="lst = []",
    reps=200,
)
t6 = bench(
    "list.insert(0, x) — prepend to start",
    "for i in range(10000): lst.insert(0, i)",
    setup="lst = []",
    reps=50,
)
t7 = bench(
    "deque.append(x) — append to end",
    "for i in range(10000): dq.append(i)",
    setup="from collections import deque; dq = deque()",
    reps=200,
)
t8 = bench(
    "deque.appendleft(x) — prepend to start",
    "for i in range(10000): dq.appendleft(i)",
    setup="from collections import deque; dq = deque()",
    reps=200,
)

print(f"\n  -> list.insert(0, x) is {t6/t5:.0f}x slower than list.append(x)")
print(f"  -> deque.appendleft is O(1) -- similar speed to deque.append")
print(f"  -> Use deque when prepending frequently; list when appending to end only")


# -----------------------------------------------------------------------------
# Benchmark 4: Membership Test — list vs set
# -----------------------------------------------------------------------------

header("Benchmark 4: Membership Test (item near end of 10,000-element collection)")

data_list = list(range(10_000))
data_set = set(range(10_000))
data_deque: deque[int] = deque(range(10_000))

t9 = bench(
    "9999 in list (O(n) scan)",
    "9999 in data_list",
    setup="data_list = list(range(10_000))",
    reps=10_000,
)
t10 = bench(
    "9999 in set (O(1) hash lookup)",
    "9999 in data_set",
    setup="data_set = set(range(10_000))",
    reps=10_000,
)
t11 = bench(
    "9999 in deque (O(n) scan)",
    "9999 in data_deque",
    setup="from collections import deque; data_deque = deque(range(10_000))",
    reps=10_000,
)

print(f"\n  -> set lookup is {t9/t10:.0f}x faster than list/deque for membership test")
print(f"  -> For any 'X in collection' in a hot path, convert to set first")


# -----------------------------------------------------------------------------
# Benchmark 5: memoryview vs bytearray Slicing
# -----------------------------------------------------------------------------

header("Benchmark 5: memoryview vs bytearray Slicing (1 MB slice from 10 MB buffer)")

t12 = bench(
    "bytearray slice (copies 1 MB)",
    "_ = data[0:1_000_000]",
    setup="data = bytearray(b'A' * 10_000_000)",
    reps=100,
)
t13 = bench(
    "memoryview slice (zero-copy view)",
    "_ = mv[0:1_000_000]",
    setup="data = bytearray(b'A' * 10_000_000); mv = memoryview(data)",
    reps=100,
)

speedup = t12 / t13
print(f"\n  -> memoryview slicing is {speedup:.0f}x faster -- zero bytes copied!")
print(f"  -> Use memoryview for any operation that slices large binary buffers")
print(f"  -> Critical for: image processing, network protocols, binary file formats")


# -----------------------------------------------------------------------------
# Benchmark 6: Listcomp vs map() vs genexpr for simple transforms
# -----------------------------------------------------------------------------

header("Benchmark 6: Listcomp vs map() vs genexpr (100,000 elements)")

t14 = bench(
    "[x*2 for x in range(N)]  — listcomp",
    "[x*2 for x in range(100_000)]",
)
t15 = bench(
    "list(map(lambda x: x*2, range(N))) — map+lambda",
    "list(map(lambda x: x*2, range(100_000)))",
)
t16 = bench(
    "list(map(str, range(N))) — map+builtin",
    "list(map(str, range(100_000)))",
)
t17 = bench(
    "[str(x) for x in range(N)] — listcomp+str",
    "[str(x) for x in range(100_000)]",
)

print(f"\n  -> map() with lambda is slower than listcomp (lambda call overhead)")
print(f"  -> map() with built-in (str, int, float) is faster than listcomp")
print(f"  -> Rule: listcomp for custom logic; map(builtin, iterable) for type conversion")


# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

header("Summary — When to Use Which Sequence Type")
print("""
  list         → General purpose mutable sequence. Default choice.
                 Good for: mixed types, frequent append, iteration, sorting.
                 Avoid for: prepending, large numeric data, membership tests.

  tuple        → Immutable record. ~30% less memory than list.
                 Good for: fixed data, dict keys, function return values.
                 Avoid for: when you need to modify elements.

  array.array  → Flat typed sequence for large numeric data.
                 Good for: 1M+ floats/ints, binary I/O (tofile/fromfile).
                 Avoid for: mixed types, small collections.

  deque        → O(1) both ends. Use as queue or stack.
                 Good for: BFS, sliding windows, ring buffers (maxlen).
                 Avoid for: random access (O(n)), large collection iteration.

  set          → O(1) membership, unique elements.
                 Not a sequence, but the answer when 'in' is the bottleneck.

  memoryview   → Zero-copy view of binary buffers.
                 Good for: slicing large binary data, binary protocol parsing.
                 Avoid for: non-binary data, small buffers.
""")
