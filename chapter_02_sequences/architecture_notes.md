# Chapter 2 — Architecture Notes: Sequences

## Why Python Has So Many Sequence Types

Python's sequence zoo exists because **different use cases have fundamentally different performance and memory requirements**. A single "array" type would be either slow, memory-wasteful, or restrictive.

### The Design Continuum

```
                Flexibility ←──────────────────→ Efficiency
                (any type, easy to use)         (typed, memory-compact)

list ─────── tuple ─────── array.array ─────── numpy.ndarray
 │               │               │                    │
 mutable      immutable       typed flat           typed + BLAS
 any type     any type        single C type        vectorized ops
 28MB/1M     20MB/1M         8MB/1M float          8MB/1M float
 floats       floats                                (+ SIMD)
```

The existence of `array.array` lets Python compete with C for memory layout without requiring NumPy.

---

## The Buffer Protocol Architecture

`memoryview` exposes Python's **buffer protocol** — a C-level interface (`Py_buffer` struct) that allows objects to share memory without copying.

```
Buffer Protocol Participants:
  bytearray, bytes, array.array, numpy.ndarray

              ┌─────────────────────┐
              │   Raw Memory Block  │  (actual bytes in C)
              └────────┬────────────┘
                       │ exposes via buffer protocol
              ┌────────▼────────────┐
              │    memoryview       │  (Python view object)
              └─────────────────────┘
                    │         │
               slicing    .cast()
              (zero-copy)  (reinterpret)
```

The buffer protocol is why `socket.recv_into(buffer)` can write directly into a bytearray without an intermediate allocation. It's why NumPy arrays can be passed to C extension functions with zero copying.

---

## CPython List Growth Policy — Why Not 2x?

Java's `ArrayList` grows by 1.5x (some versions 2x). Python grows by approximately 1.125x (1/8 of current size).

**Python's reasoning** (from CPython commit history):
1. **Memory pressure**: Python is used as a scripting language in memory-constrained environments. 2x growth means up to 50% wasted memory at any time.
2. **Amortized cost**: As long as the growth is geometric (any constant factor > 1), amortized O(1) appends are guaranteed.
3. **Observation**: Most Python lists are small (<100 elements). Over-allocating by 1/8 is sufficient to avoid frequent resizes.

**The formula**:
```python
# From CPython listobject.c
new_allocated = (newsize + (newsize >> 3) + 6) & ~3
# For n=0:   6 → 8  (rounds to nearest multiple of 4)
# For n=10:  14+2 → 16
# For n=100: 112+2 → 112
# For n=1000: 1125+2 → 1128
```

The `& ~3` rounds up to the nearest multiple of 4 to align with common CPU cache line sizes.

---

## Timsort — Why Python's Sort Is Exceptional

Python uses **Timsort** (Tim Peters, 2002), which:
- Identifies "runs" (already-sorted sub-sequences)
- Merges runs with an optimized merge algorithm
- Falls back to binary insertion sort for very small runs

**Complexity**:
- Best case: O(n) — nearly-sorted data (natural runs detected)
- Average/worst case: O(n log n)

**Why it beats pure mergesort in practice**:
Real-world data has structure. A log file sorted by timestamp is already mostly sorted — Timsort exploits this, while a theoretical sort ignores it.

**Stability**: Timsort is stable — equal elements maintain their relative order. This matters for multi-key sorts:
```python
# Sort by department first, then by name within department
employees.sort(key=lambda e: e.name)    # Primary sort by name (stable)
employees.sort(key=lambda e: e.dept)    # Now sort by dept — names stay ordered within dept
```

---

## Design Tradeoffs: Immutability in Tuples

The decision to make tuples immutable is a **semantic constraint**, not just a technical limitation.

Tuples communicate intent: "this group of values forms a single record; the structure should not change."

**Memory benefit**: Python can intern short tuples (cache them for reuse). Python 3.9+ interns tuples of small integers and other immutable types. `(1, 2, 3)` evaluated multiple times may refer to the same object.

**Hash benefit**: Tuples of hashable elements are themselves hashable — usable as dict keys or in sets. This is critical for:
- Multi-dimensional dictionaries: `lookup[(row, col)] = value`
- Memoization: `cache[tuple(args)] = result`
- Counting unique configurations

---

## Why Slicing Creates Copies (By Default)

When you slice a `list`, Python creates a new list with new references to the same objects. This is a deliberate safety choice:

```python
original = [1, 2, 3, 4, 5]
view = original[1:4]  # New list: [2, 3, 4]
view[0] = 99          # Modifies view, not original
```

If slices were views (like NumPy arrays), modifying `view[0]` would silently modify `original[1]`. For general Python lists containing heterogeneous objects, this would be extremely surprising and error-prone.

**NumPy made the opposite choice**: `arr[1:4]` returns a view, not a copy. This is appropriate for homogeneous numeric arrays where zero-copy slicing is critical for performance. NumPy compensates with explicit `.copy()` when you need independence.

**`memoryview` also returns views**: Appropriate because it's designed for binary data processing where zero-copy is the whole point.
