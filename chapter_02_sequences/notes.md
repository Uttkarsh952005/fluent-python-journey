# Chapter 2 — Notes: An Array of Sequences

## Sequence Taxonomy

```
Python Sequences
├── Container sequences (store references to Python objects)
│   ├── list        — mutable, dynamic array
│   ├── tuple       — immutable, positional record
│   └── deque       — mutable, doubly-linked blocks
│
└── Flat sequences (store C values directly, no Python object per element)
    ├── str         — immutable Unicode (UTF-8 decoded to UCS-1/2/4 internally)
    ├── bytes       — immutable binary
    ├── bytearray   — mutable binary
    ├── array.array — typed numeric (b, h, i, f, d, etc.)
    └── memoryview  — view of binary data (no own storage)
```

## Key Sequence Operations

| Operation | list | tuple | str | array | deque |
|-----------|------|-------|-----|-------|-------|
| `len(s)` | O(1) | O(1) | O(1) | O(1) | O(1) |
| `s[i]` | O(1) | O(1) | O(1) | O(1) | O(n) |
| `s[i:j]` | O(k) | O(k) | O(k) | O(k) | O(k) |
| `s + t` | O(n+m) | O(n+m) | O(n+m) | O(n+m) | O(k) |
| `x in s` | O(n) | O(n) | O(n) | O(n) | O(n) |
| `s.append(x)` | O(1)* | N/A | N/A | O(1)* | O(1) |
| `s.insert(0,x)` | O(n) | N/A | N/A | O(n) | O(1) |
| `s.pop()` | O(1) | N/A | N/A | O(1) | O(1) |
| `s.pop(0)` | O(n) | N/A | N/A | O(n) | O(1) |
| `s.sort()` | O(n log n) | N/A | N/A | N/A | N/A |

*Amortized O(1) — occasional O(n) resize.

## List Comprehension Syntax Patterns

```python
# Filter
[x for x in iterable if condition(x)]

# Transform
[f(x) for x in iterable]

# Filter + transform
[f(x) for x in iterable if condition(x)]

# Nested (Cartesian product)
[(x, y) for x in range(3) for y in range(3)]

# Conditional expression (replace, not filter)
[x if condition else default for x in iterable]
```

## Slicing Reference

```python
s[start:stop:step]

# Defaults:
# start=0, stop=len(s), step=1

# Common patterns:
s[:]       # full copy
s[::-1]    # reversed
s[::2]     # every other element
s[-3:]     # last 3
s[:-3]     # all but last 3
s[1:-1]    # all but first and last

# Named slices:
FIELD = slice(0, 5)
data[FIELD]  # equivalent to data[0:5]
```

## array.array Type Codes

| Code | C Type | Python Type | Size |
|------|--------|------------|------|
| `'b'` | signed char | int | 1 byte |
| `'B'` | unsigned char | int | 1 byte |
| `'h'` | signed short | int | 2 bytes |
| `'H'` | unsigned short | int | 2 bytes |
| `'i'` | signed int | int | 2+ bytes |
| `'l'` | signed long | int | 4+ bytes |
| `'f'` | float | float | 4 bytes |
| `'d'` | double | float | 8 bytes |

## Sorting Key Functions

```python
# By attribute
sorted(objects, key=lambda o: o.name)

# By multiple fields (tuple comparison)
sorted(objects, key=lambda o: (o.category, o.name))

# Using operator.attrgetter (faster than lambda)
from operator import attrgetter
sorted(objects, key=attrgetter("category", "name"))

# Using operator.itemgetter for tuples/dicts
from operator import itemgetter
sorted(records, key=itemgetter(1, 0))  # sort by [1] then [0]

# Reverse
sorted(items, reverse=True)

# Stable: equal elements preserve original order
```

## deque Maxlen — Ring Buffer Pattern

```python
from collections import deque

# Fixed-size sliding window:
window = deque(maxlen=5)
for item in data_stream:
    window.append(item)  # Old items auto-evicted when maxlen is reached
    # window always contains the last 5 items
```

## Vocabulary

| Term | Definition |
|------|-----------|
| **Container sequence** | Stores references to Python objects (any type) |
| **Flat sequence** | Stores C values directly (single type, memory-efficient) |
| **Over-allocation** | list reserves extra capacity for future appends |
| **Buffer protocol** | C-level interface for zero-copy memory sharing |
| **memoryview** | Python object exposing the buffer protocol |
| **Timsort** | Python's sort algorithm — hybrid merge/insertion sort |
| **Stable sort** | Equal elements maintain their original relative order |
| **Generator expression** | Lazy version of list comprehension, yields one at a time |
| **Shallow copy** | New container, same inner objects |
| **Deep copy** | Recursively creates new copies of all nested objects |
