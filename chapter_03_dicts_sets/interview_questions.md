# Chapter 3 — Interview Questions: Dicts and Sets

> Questions ranging from L3 (junior) to L6 (staff engineer) level.
> Each answer includes the depth expected at a senior Python interview.

---

## 🟢 L3 — Junior / Entry Level

### Q1: What is the time complexity of looking up a key in a Python dict?

**Expected answer:**
O(1) on average. Python dicts are backed by a hash table: `hash(key)` is computed,
mapped to a slot index, and the stored entry is checked. On average this is one memory
access. In the *worst* case — when all keys hash to the same slot — it degrades to O(n),
but Python's hash randomization (PYTHONHASHSEED) makes adversarial worst-case behavior
practically impossible in production.

---

### Q2: What is the difference between a `set` and a `frozenset`?

**Expected answer:**
Both are hash-table-backed collections of unique, hashable elements.

- `set` is **mutable**: supports `add()`, `remove()`, `discard()`, `pop()`, `|=`, etc.
- `frozenset` is **immutable** and **hashable**: can be used as a dict key or as an
  element of another set.

```python
fs = frozenset({1, 2, 3})
d = {fs: "group A"}        # valid — frozenset is hashable
s = set({1, 2, 3})
d = {s: "group A"}         # TypeError — set is not hashable
```

Use `frozenset` for representing unordered, fixed groups (e.g., graph edges, permission sets).

---

### Q3: How do you safely get a value from a dict when you're not sure the key exists?

**Expected answer:**
Three options with different semantics:

```python
# Option 1: .get() — returns default (None by default), no side effect
value = d.get("key", "default")

# Option 2: try/except — Pythonic for EAFP (Easier to Ask Forgiveness...)
try:
    value = d["key"]
except KeyError:
    value = "default"

# Option 3: defaultdict — auto-creates missing keys with a factory
from collections import defaultdict
dd = defaultdict(int)
dd["count"] += 1    # no check needed — starts at 0
```

Never use `if "key" in d: return d["key"]` — that's two lookups.

---

## 🟡 L4 — Mid-Level

### Q4: What is `setdefault()` and when should you use it over `get()`?

**Expected answer:**
`setdefault(key, default)` checks if `key` exists. If it does, returns the existing value.
If not, **inserts `key: default` into the dict and returns the default**.

This is different from `get()` which never modifies the dict.

Use `setdefault()` when you want to **build nested structures** in a single lookup:

```python
# Building an inverted index — classic setdefault use case
index = {}
for word in words:
    for char in word:
        index.setdefault(char, []).append(word)  # one lookup, insert if needed
```

The equivalent with `get()` requires three operations:
```python
existing = index.get(char, [])   # get (or empty list)
existing.append(word)             # modify
index[char] = existing            # re-insert — second lookup!
```

---

### Q5: When would you use `OrderedDict` in Python 3.7+ when plain dicts already preserve insertion order?

**Expected answer:**
Two remaining reasons:

1. **`move_to_end(key, last=True/False)`** — O(1) reordering (backed by a doubly-linked
   list in C). Plain dict has no equivalent. Useful for LRU cache implementations.

2. **Order-aware equality** — `OrderedDict({'a':1,'b':2}) != OrderedDict({'b':2,'a':1})`.
   Plain dicts consider these equal regardless of insertion order.

```python
from collections import OrderedDict

od = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
od.move_to_end("a")               # O(1): ['b', 'c', 'a']
od.move_to_end("c", last=False)   # O(1): ['c', 'b', 'a']
```

For all other use cases, plain dict is sufficient and slightly faster.

---

### Q6: Explain the difference between `dict.keys() & other.keys()` and writing a loop.

**Expected answer:**
`dict.keys()` returns a `dict_keys` view object, which implements set operations
(`&`, `|`, `-`, `^`) directly. The view is backed by the dict's own hash table, so
set operations avoid constructing intermediate data structures.

```python
common = a.keys() & b.keys()   # intersection — returns a plain set
only_in_a = a.keys() - b.keys()
```

This is equivalent to:
```python
common = set()
for k in a:
    if k in b:        # O(1) because b is a dict
        common.add(k)
```

Both are O(min(len(a), len(b))) on average. The set operation is preferred for clarity.
Note: the return type is `set`, not `dict_keys`.

---

## 🔴 L5 — Senior

### Q7: What is the `__hash__` / `__eq__` contract and why does Python nullify `__hash__` when you define `__eq__`?

**Expected answer:**
The contract: **if `a == b`, then `hash(a)` must equal `hash(b)`**.

This is required for correct dict and set behavior. When you look up `d[key]`, Python first
checks hash equality (fast, integer comparison), then key equality (potentially expensive).
If equal objects had different hashes, equal keys would map to different slots and
`d[key1]` would never find `key2`'s entry — silent data corruption.

When you define `__eq__` without `__hash__`, Python cannot guarantee the contract is
satisfied (your `__eq__` might use mutable fields). So Python sets `__hash__ = None`,
making the object unhashable. This is conservative but correct:
**fail loudly with TypeError rather than silently corrupt a dict**.

The fix: implement `__hash__` using the *same immutable fields* as `__eq__`:
```python
def __hash__(self):
    return hash((self.x, self.y))   # same fields as __eq__
```

---

### Q8: What's the practical difference between `defaultdict` and implementing `__missing__` on a `dict` subclass?

**Expected answer:**
`defaultdict` is implemented in C and calls `default_factory()` with no arguments.
`__missing__` is a Python hook that gives you full control — you receive the key as an
argument and can implement arbitrary logic.

Key behavioral difference: `defaultdict` can be implemented entirely via `__missing__`,
but `defaultdict` stores the factory as an attribute (`default_factory`), which
means you can change it at runtime or set it to `None` to disable the behavior.

`__missing__` is more flexible:
```python
class StrKeyDict(dict):
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)      # real missing str key — stop
        return self[str(key)]        # try string version of non-str key
```

This logic (key transformation on lookup) isn't possible with `defaultdict`.

Also: `__missing__` is only called by `__getitem__` (`d[key]`), not by `.get()`.
`defaultdict` has the same limitation — `dd.get("missing")` returns `None`, not the default.

---

## 🟣 L6 — Staff Engineer / Python Internals

### Q9: Explain Python's compact dict layout (introduced in 3.6) and why it preserves insertion order as a side effect.

**Expected answer:**
Before Python 3.6, dict used a single sparse array of `(hash, key, value)` triples.
To keep collisions low (~2/3 load), 1/3+ of slots were always empty — wasting memory.

CPython 3.6 (Raymond Hettinger's redesign) split this into two structures:

```
Indices table (sparse, small integers):
  [ -1, 2, -1, 0, -1, 1, ... ]   ← maps hash%size to entry index

Entries array (dense, insertion order):
  [ (hash0, key0, val0), (hash1, key1, val1), (hash2, key2, val2) ]
```

The sparse part is now just an array of small integers (1–4 bytes each) rather than
full (hash, key, val) tuples. Memory savings: ~20–25%.

**Insertion order preservation** is a free side effect: the dense entries array is
appended to in order. When iterating, Python walks the entries array sequentially —
in insertion order. No extra bookkeeping needed.

Python 3.7 made this an official language guarantee (not just a CPython implementation
detail), once PyPy and other implementations adopted the same approach.

---

### Q10: Why is `hash(1) == hash(1.0)` true in Python?

**Expected answer:**
Because `1 == 1.0` is true, and the hash contract requires that equal objects have
equal hashes. Python enforces this for numeric types by defining a common hash function
for all numeric types: for integers that fit exactly as floats (like 1), the hash
is computed as `hash(float(n))`. More precisely, both `hash(1)` and `hash(1.0)` use
the same hash formula:

```python
hash(1)    # 1
hash(1.0)  # 1  — same!
```

The general rule from the Python docs: "The only required property is that objects
which compare equal have the same hash value." Numeric types implement this across
`int`, `float`, `complex`, `Decimal`, and `Fraction` — any numeric equality produces
equal hashes.

**Consequence**: You can use int or float interchangeably as dict keys, and they'll
find each other's values:
```python
d = {1: "int key"}
d[1.0]   # "int key" — 1 == 1.0 and hash(1) == hash(1.0)
```

---

*Depth check: senior engineers should be able to explain WHY, not just WHAT.
"Dicts are O(1)" is L3. "Here's why O(1) degrades to O(n) and why Python prevents it" is L5.*
