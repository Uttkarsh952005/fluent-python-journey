# Chapter 2 — Interview Questions: Sequences

> L3 through L6. Each answer goes beyond surface-level to show systems thinking.

---

## 🟢 L3 — Junior

### Q1: What is the difference between a list and a tuple in Python?

**Expected answer (senior depth):**
The *obvious* difference: lists are mutable, tuples are immutable.

The *deeper* difference: **they serve different semantic roles**.

- **List**: A homogeneous, mutable collection of items of the same conceptual type (`[user1, user2, user3]`). The length can vary.
- **Tuple**: A heterogeneous, fixed record where *position has meaning* (`("Tokyo", "JP", 36.933)`). Think of it as a poor man's struct.

**Memory**: Tuples are ~30% smaller than equivalent lists because:
1. Lists over-allocate (reserve extra capacity for future appends)
2. Tuples are compact — allocated at exact size

**Performance**: Tuple construction is slightly faster than list. Tuple literal `(1, 2, 3)` is a single constant in the bytecode; list `[1, 2, 3]` requires building a list at runtime.

---

### Q2: When would you use `deque` instead of `list`?

**Expected answer:**
When you need **O(1) operations at both ends**.

`list.insert(0, x)` and `list.pop(0)` are O(n) because every element must shift. `deque.appendleft(x)` and `deque.popleft()` are O(1).

Use `deque` for:
- Queues (FIFO) — `appendleft` + `pop` or `append` + `popleft`
- Stacks (LIFO) — `append` + `pop` (same as list, but deque is more explicit)
- Sliding windows — `deque(maxlen=N)` auto-evicts oldest element
- Breadth-first search — O(1) queue operations matter at scale

**Don't** use `deque` for random access — `deque[n]` is O(n), not O(1) like list.

---

## 🟡 L4 — Mid-Level

### Q3: What does `a += b` do differently for lists vs tuples?

**Expected answer:**
For **lists** (mutable): `a += b` calls `a.__iadd__(b)`, which modifies `a` *in place* and returns `a`. The variable still points to the same object. `id(a)` is unchanged before and after.

For **tuples** (immutable): `a += b` creates a *new tuple* containing all elements of `a` and `b`, then rebinds the variable `a` to this new object. `id(a)` changes.

**The subtle bug** (from the book):
```python
t = ([1, 2], [3, 4])
t[0] += [5, 6]
```
This:
1. Calls `t[0].__iadd__([5, 6])` → modifies the list in place (succeeds!)
2. Tries `t[0] = result` → fails with `TypeError` (tuple is immutable)
3. The list is *already modified* from step 1

Result: the operation raises `TypeError` but *also* mutates the list inside the tuple. This is documented CPython behavior that surprises even experienced developers.

**Lesson**: Never use augmented assignment on mutable objects stored in tuples.

---

### Q4: What is `memoryview` and when would you use it?

**Expected answer:**
`memoryview` exposes the **buffer protocol** — it provides a view into the raw memory of another object (bytearray, bytes, array.array, NumPy array) without copying it.

Key properties:
- `mv[0:1000]` creates a view, not a copy — O(1), not O(n)
- `mv.cast("H")` reinterprets the same bytes as a different C type (e.g., unsigned shorts)
- Modifying `mv[i] = x` modifies the underlying buffer in place

**When to use it:**
1. Slicing large binary buffers (network packets, image data, binary file formats)
2. Passing binary data between C extensions without copies
3. Implementing binary protocols where you need to inspect different sections of a buffer without allocation

**Real-world example**: Parsing a binary network packet header — you can create views for each field without allocating 4+ separate byte objects.

---

## 🔴 L5 — Senior

### Q5: How does Python's list grow dynamically? What's the growth policy and why?

**Expected answer:**
Python lists are dynamic arrays. When the backing C array is full, Python allocates a new, larger array and copies all elements.

The growth formula (from CPython `listobject.c`):
```c
new_size = (current_size + (current_size >> 3) + 6) & ~3
```
This gives approximately 1.125x growth (1/8 of current size + rounding). For a list of 10, this grows to ~14; for 1000 → ~1127.

**Why not 2x growth (like Java ArrayList)?**
- 2x wastes more memory — at worst, you have 50% empty slots
- Python's conservative growth reduces memory usage at the cost of slightly more frequent copies
- The amortized O(1) guarantee holds regardless — as long as growth is geometric

**Pre-allocation insight**: If you know the final size, `[None] * n` is much faster than repeated `append()` — it allocates once. Similarly, `list(range(n))` avoids repeated resizing.

---

### Q6: Explain the sequence protocol. What's the minimal interface to make an object work with `for`, `in`, `len()`, `random.choice()`, and `reversed()`?

**Expected answer:**

| Feature | Required Methods |
|---------|----------------|
| `for x in obj` | `__iter__` OR `__getitem__(int)` |
| `x in obj` | `__contains__` OR `__getitem__` fallback |
| `len(obj)` | `__len__` |
| `random.choice(obj)` | `__len__` + `__getitem__` |
| `reversed(obj)` | `__reversed__` OR (`__len__` + `__getitem__`) |

**Minimal "full sequence"**: `__len__` + `__getitem__`. This gives you all of the above for free via Python's fallback chain.

**Why provide `__contains__` explicitly?**
The default `in` operator falls back to a linear scan via `__getitem__`. If your data structure supports O(1) lookup (like a hash-based structure), you should override `__contains__` to avoid O(n) scans.

---

## 🟣 L6 — Staff Engineer

### Q7: Why does `list[i]` have O(1) access while `deque[i]` has O(n)? Explain the underlying data structures.

**Expected answer:**
`list` is a **dynamic array** — a contiguous block of memory storing pointers. `list[i]` computes `base_address + i * pointer_size` — one multiplication and one memory read. O(1), CPU-cache-friendly.

`deque` is a **doubly-linked list of fixed-size blocks** (each block holds ~64 elements). To access `deque[i]`, Python must traverse block-by-block from the nearest end. For the middle element of a large deque, this traverses O(n/64) = O(n) blocks.

**CPython deque implementation**: Each block is a `dequeblock` struct containing an array of 64 `PyObject*` pointers. The deque struct has `leftblock`, `rightblock`, and `leftindex`/`rightindex` to track positions. Appending to the right means incrementing `rightindex`; when it hits 64, allocate a new `rightblock`.

**The tradeoff**: List is better for random access + end appends. Deque is better for O(1) both-end operations + bounded ring buffers.

**Interview follow-up**: "How would you implement O(1) random access with O(1) push/pop at both ends?" → Answer: sqrt decomposition (not in stdlib; use for pathological cases).
