# Chapter 2 — An Array of Sequences

<div align="center">

![Status](https://img.shields.io/badge/Status-Active%20Deep%20Dive-FF9800?style=flat-square)
![Concepts](https://img.shields.io/badge/Concepts-Sequences%20%7C%20Slicing%20%7C%20memoryview%20%7C%20deque-FF6B35?style=flat-square)

</div>

> *"The Python standard library offers a rich selection of sequence types implemented in C: in addition to lists, there are the tuple, str, bytes, bytearray, memoryview, and array.array types."*
> — Luciano Ramalho, Fluent Python

---

## 🧠 What This Chapter Is Really About

Chapter 2 is deceptively broad. On the surface it teaches you list comprehensions and slicing. But the deeper lesson is:

**Python has a rich taxonomy of sequence types, each with distinct memory models, performance characteristics, and appropriate use cases. Choosing the wrong one is a real performance and correctness mistake.**

The key mental model to build:

```
Sequences
├── Container sequences (hold references to any type)
│   ├── list        — mutable, dynamic array, O(1) append amortized
│   ├── tuple       — immutable, fixed-size, ~30% less memory than list
│   └── deque       — mutable, O(1) both ends, O(n) middle
│
└── Flat sequences (hold values directly in memory, C array)
    ├── str         — immutable Unicode text
    ├── bytes       — immutable binary
    ├── bytearray   — mutable binary
    ├── array.array — typed numeric array, 4x less memory than list
    └── memoryview  — zero-copy view of binary data
```

**Container sequences** store *pointers* to Python objects. Each element is a full Python object on the heap.

**Flat sequences** store the *values themselves* in a contiguous C array. No Python object overhead per element — much more memory-efficient for numeric data.

---

## 📐 Core Concepts

### 1. List Comprehensions vs Generator Expressions

**List comprehensions** are *eager* — they build the entire list in memory:
```python
squares = [x**2 for x in range(1000)]  # 1000 ints in memory immediately
```

**Generator expressions** are *lazy* — they yield one value at a time:
```python
squares = (x**2 for x in range(1000))  # No values computed yet
```

**When to use which:**
- Need to iterate once and discard → **genexpr** (lower memory)
- Need to iterate multiple times → **listcomp** (avoids recomputation)
- Pass to function that accepts iterator → **genexpr** (e.g., `sum(x**2 for x in r)`)
- Need indexing / slicing → **listcomp** (generators don't support it)

### 2. Slicing — More Than `[start:stop]`

Python's slice object is first-class:
```python
s = slice(1, 10, 2)  # slice(start, stop, step)
my_list[s]           # equivalent to my_list[1:10:2]
```

**The slice assignment protocol**: Any object can support slice assignment by implementing `__setitem__` with a slice argument.

**How Python computes indices for slices:**
```python
# For s[1:10:2] on a list of length 15:
# start, stop, step = slice(1, 10, 2).indices(15)
# → (1, 10, 2) — indices() normalizes negative indices, clamps to bounds
```

### 3. `array.array` — When Lists Are Wasteful

```python
import array
import sys

# A list of 1 million floats:
lst = [float(i) for i in range(1_000_000)]
sys.getsizeof(lst) + sum(sys.getsizeof(x) for x in lst[:100]) * 10000
# ≈ 28 MB (each float is a Python object: ~28 bytes)

# An array of 1 million floats:
arr = array.array("d", range(1_000_000))  # 'd' = C double
sys.getsizeof(arr)  # ≈ 8 MB (8 bytes per double, no Python object overhead)
```

`array.array` stores raw C values — no Python float objects. The tradeoff: elements must all be the same C type (`'b'`, `'h'`, `'i'`, `'f'`, `'d'`, etc.).

### 4. `memoryview` — Zero-Copy Binary Operations

`memoryview` lets you slice and manipulate binary data **without copying**. This is critical for performance when working with large buffers (network data, image pixels, binary file formats).

```python
data = bytearray(b"Hello, World!")
mv = memoryview(data)

# Modify bytes 7-12 without copying the rest:
mv[7:12] = b"NumPy"  # Zero copy — modifies data in place

# Reinterpret the same memory as 16-bit integers:
nums = array.array("B", range(256))
mv = memoryview(nums)
shorts = mv.cast("H")  # Reinterpret as unsigned 16-bit, still zero-copy
```

### 5. Tuples as Records vs Tuples as Immutable Lists

Tuples play two roles in Python, and understanding both is important:

**As records** (with semantic positional meaning):
```python
city = ("Tokyo", "JP", 36.933, (35.689722, 139.691667))
# Each position means something: name, country, population, coordinates
```

**As immutable lists** (when you just need immutability):
```python
CONSTANTS = (1, 2, 3)  # Better than [1, 2, 3] if it won't change
```

The book argues: when using tuples as records, prefer `collections.namedtuple` or `typing.NamedTuple` for self-documentation.

### 6. `deque` — When `list.insert(0, x)` Is Your Bottleneck

```
list.insert(0, x)  → O(n) — must shift all elements right
list.append(x)     → O(1) amortized
list.pop(0)        → O(n) — must shift all elements left
list.pop()         → O(1)

deque.appendleft(x) → O(1)
deque.append(x)     → O(1)
deque.popleft()     → O(1)
deque.pop()         → O(1)
```

`deque` is implemented as a doubly-linked list of fixed-size blocks — not a single contiguous array. This gives O(1) at both ends but O(n) random access.

---

## 📊 Performance Summary

| Operation | `list` | `tuple` | `array.array` | `deque` |
|-----------|--------|---------|--------------|---------|
| Memory (1M floats) | ~28 MB | ~8 MB | ~8 MB | ~40 MB |
| Append end | O(1) amortized | N/A | O(1) amortized | O(1) |
| Prepend | O(n) | N/A | O(n) | O(1) |
| Random access | O(1) | O(1) | O(1) | O(n) |
| Search (`in`) | O(n) | O(n) | O(n) | O(n) |
| Sort | O(n log n) | N/A | N/A | N/A |

*See `benchmarks.py` for measured numbers with methodology.*

---

## 🔬 CPython Internals

### How Python Lists Grow

Python lists are dynamic arrays. When you `append()` to a full list, Python allocates a **larger array** and copies all elements:

```c
// Growth pattern (from CPython listobject.c):
// new_allocated = (newsize + (newsize >> 3) + 6) & ~3
// For a list of 10 → grows to 14, 18, 25, 35, 46...
```

This geometric growth (approximately 1.125x) means amortized O(1) appends, but instantaneous O(n) resizes happen occasionally.

**Why this matters**: Pre-allocating with `list(range(n))` or `[None] * n` avoids repeated resizing when you know the size upfront.

### How Slicing Creates New Objects

```python
lst = [1, 2, 3, 4, 5]
sliced = lst[1:3]  # Creates a NEW list: [2, 3]
```

Slicing a list **always creates a copy**. For large lists, this can be expensive. `memoryview` avoids this for binary sequences.

---

## 📁 Files in This Chapter

| File | Description |
|------|-------------|
| [`examples.py`](examples.py) | Comprehensions, memoryview, slicing, augmented assignment |
| [`exercises.py`](exercises.py) | Original exercises on sequences and performance |
| [`mini_project.py`](mini_project.py) | Data pipeline using sequences optimally |
| [`benchmarks.py`](benchmarks.py) | Memory + speed: list vs tuple vs array vs deque |
| [`notes.md`](notes.md) | Structured reference: sequence type taxonomy |
| [`pitfalls.md`](pitfalls.md) | Mutable defaults, list multiplication, shallow copy |
| [`interview_questions.md`](interview_questions.md) | Senior-level Q&A on sequences |
| [`architecture_notes.md`](architecture_notes.md) | Why Python has so many sequence types |

---

## 🔗 Related

- **Chapter 3** (this repo): Dicts and Sets — non-sequence collections
- **Chapter 6** (this repo): Object References — shallow vs deep copy in depth
- [python-performance-lab](https://github.com/Uttkarsh952005/python-performance-lab): Full benchmark suite for all sequence types
- [python-internals-playground](https://github.com/Uttkarsh952005/python-internals-playground): `memoryview` and buffer protocol deep dive
