# Chapter 3 — Dicts and Sets

<div align="center">

![Status](https://img.shields.io/badge/Status-Active-4CAF50?style=flat-square)
![Concepts](https://img.shields.io/badge/Concepts-Hash%20Tables%20%7C%20Dict%20Internals%20%7C%20Set%20Operations-FF6B35?style=flat-square)

</div>

> *"The dict type is not only widely used in our programs, but also a key part of the Python implementation."*
> — Luciano Ramalho, Fluent Python

---

## What this chapter is really about

Most Python programmers know that dicts are fast and sets test membership in O(1). Fewer understand *why*, or what the limits of that guarantee are. This chapter is about understanding the hash table that powers both structures — how keys are stored, what "hashable" actually means contractually, what happens during a collision, and why mutable objects can't be dict keys.

---

## Hash Table Internals

A Python dict is a hash table. The simplified model:

```
key  →  hash(key)  →  hash % table_size  →  slot index  →  (key, value) stored there
```

**Two-phase lookup:**
1. Compute `hash(key)` — an integer fingerprint
2. Map that hash to a slot via `hash % table_size`
3. Check if the slot's stored key matches (`==`) — handles collisions
4. If not, probe further (Python uses pseudo-random probing, not linear)

**Python 3.6+ compact dict layout** (Raymond Hettinger's redesign):

```
Old layout (pre-3.6):
  [ (hash, key, value), (hash, key, value), ... ]   ← one big sparse array

New compact layout (3.6+):
  indices:  [ 2, -1, 0, -1, 1, ... ]                ← small, sparse array of slot pointers
  entries:  [ (hash,key,val), (hash,key,val), ... ]  ← dense array, insertion order preserved
```

Benefits of compact layout:
- **Memory**: ~20–25% smaller on average (sparse array is tiny integers, not full tuples)
- **Cache**: dense entries array fits better in CPU cache lines
- **Order**: insertion order preserved as a *side-effect* of the dense entries array

This is why dict ordering is guaranteed from Python 3.7+. It's not an accident — it fell out of the memory optimization.

**Load factor**: Python resizes the hash table when it's ~2/3 full. Resize = allocate a table 4x larger, rehash everything. This keeps collision probability low and ensures O(1) average lookup.

---

## Hashability

The `__hash__` / `__eq__` contract is the bedrock of both dicts and sets.

**The contract:**
```python
# If a == b, then hash(a) MUST equal hash(b)
# The reverse is not required — hash collisions are allowed
```

**Built-in hashability rules:**

| Type | Hashable? | Why |
|------|-----------|-----|
| `int`, `float`, `str`, `bytes` | ✅ | Immutable, hash is stable |
| `tuple` | ✅ if all elements hashable | Immutable container |
| `frozenset` | ✅ | Immutable set |
| `list` | ❌ | Mutable — hash would change |
| `dict` | ❌ | Mutable |
| `set` | ❌ | Mutable |
| Custom class (no `__eq__`) | ✅ | Uses `id()` as hash |
| Custom class (defines `__eq__`) | ❌ unless `__hash__` also defined | Python nullifies `__hash__` |

**The nullification rule** is subtle: when you define `__eq__` on a class, Python sets `__hash__ = None` automatically. This makes instances unhashable. You *must* explicitly define `__hash__` if you also define `__eq__`.

```python
class Point:
    def __init__(self, x, y): self.x, self.y = x, y
    def __eq__(self, other): return (self.x, self.y) == (other.x, other.y)
    # No __hash__ defined → Point.__hash__ is None → hash(Point(1,2)) raises TypeError
```

**Correct pattern:** hash the same fields you use in `__eq__`, using a tuple:

```python
def __hash__(self) -> int:
    return hash((self.x, self.y))
```

---

## Missing Key Handling

Four strategies, each communicating different intent:

| Strategy | Use when | Gotcha |
|----------|----------|--------|
| `d.get(key, default)` | One-off safe access | Default is always evaluated |
| `d.setdefault(key, [])` | Building nested structures | One lookup instead of two |
| `defaultdict(factory)` | Always-present defaults | Accessing a missing key *creates* it |
| `__missing__` override | Custom subclass logic | Only triggered by `d[key]`, not `d.get()` |

The `__missing__` distinction is the most misunderstood: `dict.get()` does **not** call `__missing__`. Only `__getitem__` (`d[key]`) does.

---

## Set Operations

Sets use the same hash table machinery as dicts — just without values.

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b   # union: {1, 2, 3, 4, 5, 6}
a & b   # intersection: {3, 4}
a - b   # difference: {1, 2}
a ^ b   # symmetric difference: {1, 2, 5, 6}
```

**`frozenset`** is the immutable, hashable sibling. It supports all the same operations *except* mutation. Because it's hashable, it can be used as a dict key or as an element of another set — useful for representing unordered pairs, graph edges, or fixed permission groups.

```python
# Represent unordered graph edges (A-B == B-A)
edges = {frozenset({"A", "B"}), frozenset({"B", "C"})}
```

**`dict.keys()` views** support set operations directly, because keys are always unique and hashable:

```python
a_keys & b_keys   # keys common to both dicts
a_keys - b_keys   # keys only in a
```

`dict.values()` does **not** support set operations — values can repeat and may not be hashable.

---

## Performance Notes

| Operation | Dict | List | Why |
|-----------|------|------|-----|
| Lookup by key | O(1) avg | O(n) | Hash → direct slot |
| Membership test | O(1) avg | O(n) | Same |
| Insertion | O(1) avg | O(1) append | Amortized |
| Iteration | O(n) | O(n) | Same |
| Memory (10k items) | ~350KB | ~80KB | Dict has overhead per entry |

**O(1) average, O(n) worst case**: worst case requires every key to hash to the same slot (adversarial hash collision). Python 3.3+ adds hash randomization (PYTHONHASHSEED) to make this attack vector impractical in practice.

**When dict is the wrong choice:**
- You need ordered iteration by *value* → use a list of tuples or sort
- You need range queries → use `bisect` on a sorted list
- You have 3 or fewer keys checked in sequence → `in`-chain on a tuple might be faster

---

## Common Mistakes

**1. `{}` creates a dict, not a set**
```python
x = {}   # dict — everyone does this at least once
x = set()  # empty set
```

**2. Mutating a dict while iterating it**
```python
for k in d:
    del d[k]  # RuntimeError: dictionary changed size during iteration
# Fix: iterate over a copy
for k in list(d):
    del d[k]
```

**3. `defaultdict` silently creates missing keys**
```python
dd = defaultdict(list)
_ = dd["ghost"]  # Creates dd["ghost"] = [] — now "ghost" is in dd
# Use dd.get("ghost") if you don't want auto-creation
```

**4. `__missing__` not called by `get()`**
```python
class MyDict(dict):
    def __missing__(self, key): return "fallback"

d = MyDict()
d["x"]       # "fallback" ✓
d.get("x")   # None — __missing__ is never called by get()
```

**5. Unhashable type in set/dict key**
```python
s = {[1, 2]}  # TypeError: unhashable type: 'list'
# Use frozenset or tuple instead
s = {(1, 2)}
```

---

## Files

| File | Status | Description |
|------|--------|-------------|
| `README.md` | ✅ | This file |
| `examples.py` | ✅ | Annotated implementations: 7 parts covering dict internals |
| `notes.md` | ✅ | Structured reference notes |
| `exercises.py` | ✅ | Original exercises extending the concepts |
| `mini_project.py` | 📋 Planned | Word frequency / duplicate detector |
| `benchmarks.py` | 📋 Planned | Dict lookup vs list scan, set membership |
| `pitfalls.md` | 📋 Planned | Production mistakes and fixes |
| `interview_questions.md` | 📋 Planned | Senior-level Q&A |
