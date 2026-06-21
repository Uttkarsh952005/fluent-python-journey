# Chapter 3 — Architecture Notes: Dicts and Sets

Design decisions behind Python's hash table implementation — why it was built
this way, what tradeoffs were made, and what alternatives exist.

---

## Why Python Chose Hash Tables for Dicts and Sets

The fundamental alternatives for a key→value mapping are:

| Approach | Lookup | Insert | Memory | Order |
|----------|--------|--------|--------|-------|
| Sorted array + bisect | O(log n) | O(n) | Low | Sorted |
| Linked list | O(n) | O(1) | Low | Insertion |
| Hash table (Python) | O(1) avg | O(1) avg | High | Insertion (3.7+) |
| Tree (e.g., std::map) | O(log n) | O(log n) | Medium | Sorted |

Python chose hash tables for one reason: **the entire language runtime depends on
dict performance**. Every function call, every attribute lookup, every module import
touches a dict. O(log n) would make Python noticeably slower at scale.

The cost — memory overhead — is accepted because:
1. Memory is cheap; CPU cycles at tight loops are not
2. The compact layout (Python 3.6+) reduced the cost significantly
3. For memory-critical numeric data, `array.array` or numpy exist

---

## The Compact Dict Layout: A Deep Dive

**Before Python 3.6** — one sparse array:
```
hash table (size=8 for dict with 5 entries):
  slot 0: EMPTY
  slot 1: (hash_b, "beta",  2)
  slot 2: EMPTY
  slot 3: (hash_a, "alpha", 1)
  slot 4: EMPTY
  slot 5: (hash_g, "gamma", 3)
  slot 6: EMPTY
  slot 7: EMPTY
```
Problem: for N entries, the table needs ~1.5N slots (2/3 load factor).
Each slot stores 3 pointers (hash + key + value) even when empty.

**Python 3.6+ compact layout** (two arrays):
```
indices (sparse, 1–4 bytes per slot):
  [ -1, 1, -1, 0, -1, 2, -1, -1 ]

entries (dense, exactly N entries):
  [ (hash_a, "alpha", 1),   ← index 0
    (hash_b, "beta",  2),   ← index 1
    (hash_g, "gamma", 3) ]  ← index 2
```

The sparse part is now just integers (1 byte each for small dicts), not triples.
Memory savings: ~20–25% for typical dictionaries.

**Why insertion order is preserved:**
Lookup uses `indices[hash % size]` → entries[i]. New entries always append to
`entries`. Iterating the dict walks `entries` sequentially — insertion order is
intrinsic to the data structure, not an added bookkeeping layer.

Raymond Hettinger proposed this design in 2012. CPython 3.6 implemented it.
Python 3.7 made insertion-order preservation a language specification.

---

## The Collision Resolution Strategy

Python uses **open addressing with pseudo-random probing**.

When slot `hash % size` is occupied by a *different* key, the next probe is:
```
i = (5 * i + 1 + (hash >> perturbation)) % size
perturbation >>= PERTURB_SHIFT   # reduces over iterations
```

This is NOT linear probing (probe i, i+1, i+2, ...) because:
- Linear probing causes **clustering**: adjacent slots fill up, slowing future probes
- Python's formula uses the hash bits themselves to spread probes across the table
- Different initial hashes → different probe sequences → better distribution

The formula ensures every slot is eventually visited (it's a full permutation of
the table indices), so the dict never gets "stuck" even when nearly full.

---

## Why MutableMapping > dict Subclassing

Ramalho recommends subclassing `collections.UserDict` rather than `dict` directly.
The reason is subtle: built-in `dict` uses C-level shortcuts that bypass Python methods.

```python
class MyDict(dict):
    def __setitem__(self, key, value):
        print(f"Setting {key}")
        super().__setitem__(key, value)

d = MyDict(a=1)     # Does NOT call our __setitem__!
d.update({"b": 2})  # Also does NOT call our __setitem__!
d["c"] = 3          # This one DOES call our __setitem__
```

This inconsistency is because `dict.__init__` and `dict.update` call the C-level
`dict_update_common`, which inserts directly into the hash table without going
through Python's method dispatch.

`UserDict` wraps a plain `dict` in `self.data` and all methods route through Python:
```python
class UserDict(MutableMapping):
    def __init__(self, dict=None, **kwargs):
        self.data = {}
        if dict is not None:
            self.update(dict)    # calls self.__setitem__ — YOUR override!
```

**Design lesson**: When the C implementation bypasses your Python overrides, it's
not a bug — it's a deliberate speed optimization for the common case. The price is
that subclassing built-in types is tricky. Use composition (UserDict) instead.

---

## The `__missing__` Hook: Design Intent

`__missing__` was added in Python 2.5 specifically to enable `defaultdict` to be
implemented as a Python-level class (before it was added as a C built-in).

The hook has a deliberately narrow contract:
- Called ONLY by `dict.__getitem__` when a key is absent
- NOT called by `get()`, `__contains__`, `update()`, `setdefault()`, or `pop()`

This narrowness is intentional. If `__missing__` fired on every absent-key access,
you'd get auto-creation on `"key" in d`, which would break the semantics of membership
testing. The narrow contract keeps the behavior predictable.

The inconsistency across dict, UserDict, and abc.Mapping is documented in the book
(page 94) and is a known rough edge in the stdlib.

---

## Hash Randomization: Security Implication

Since Python 3.3, string and bytes hashes are salted with a random seed
(`PYTHONHASHSEED`) that's generated fresh each process start.

**Why**: Hash tables degrade to O(n) when all keys collide (same hash → same slot).
An attacker who knows Python's hash function could craft HTTP parameters or JSON keys
that all collide, causing O(n²) processing in web servers — a denial-of-service attack.
This was CVE-2011-4885 (Django, 2011).

**Consequence for engineers**:
- `hash("foo")` returns a different value in each Python process
- Dict iteration order is stable within a process but not across restarts
- Do NOT persist or transmit hash values — use `hashlib` for deterministic hashing

```python
# Wrong: relying on hash() for cross-process stable IDs
key = hash(username)          # ❌ different each run

# Right: use a cryptographic/deterministic hash
import hashlib
key = hashlib.sha256(username.encode()).hexdigest()  # ✅ stable
```

---

## Sets as First-Class Algebra

Python's set type implements the full mathematical set theory API using infix operators.
This is an intentional design: set algebra reads like math, and Python's operator
overloading makes it expressible in code.

Compare:
```python
# Imperative (what most languages offer):
common = []
for item in a:
    if item in b:
        common.append(item)

# Declarative (Python sets):
common = a & b
```

The declarative form is not just shorter — it's semantically different. `a & b`
expresses *what* you want; the loop expresses *how* to get it. As sets scale to
millions of elements, the set operation also stays O(min(|a|, |b|)) while a naive
loop with a list for `b` degrades to O(|a| × |b|).

This is why Ramalho says set operations "can reduce both the line count and the
execution time of Python programs, at the same time making code easier to read and
reason about."

---

## Key Design Tradeoffs Summary

| Decision | Tradeoff Made | Why Python Accepted It |
|----------|---------------|------------------------|
| Hash table for dict | Memory overhead | Runtime speed critical |
| Compact layout (3.6) | Code complexity | 20–25% memory savings |
| Insertion order preservation | Slightly more implementation complexity | Developer ergonomics |
| `__missing__` narrow contract | Surprising `.get()` behavior | Predictable semantics |
| Hash randomization | Cross-process instability | Security > convenience |
| Unhashable mutables | TypeError on `hash([])` | Safety > flexibility |
