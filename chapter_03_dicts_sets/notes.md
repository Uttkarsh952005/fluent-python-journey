# Chapter 3: Notes — Dicts and Sets

Structured reference notes alongside `examples.py`. These are not a summary of
the chapter — they capture the *why* behind implementation choices and the
details that trip people up in practice.

---

## Compact Dict Layout (Python 3.6+)

The most important architectural change to dict in recent Python history.

**Before 3.6** — sparse table of (hash, key, value) triples:
```
slot 0: (empty)
slot 1: (hash_b, "b", 2)
slot 2: (empty)
slot 3: (hash_a, "a", 1)
slot 4: (empty)
...
```
Problem: most slots empty. Memory wasted proportional to load factor headroom.

**3.6+ compact layout** — two arrays:
```
indices table (sparse, small integers):
  [ -1, 1, -1, 0, -1, ... ]

entries array (dense, insertion order):
  [ (hash_a, "a", 1), (hash_b, "b", 2) ]
```

The sparse indices table maps `hash % size` → position in the dense entries array.
The entries array stays compact and in insertion order.

Result: ~20-25% memory reduction. Insertion-order preservation as a free side effect.
CPython made this the guaranteed behavior in 3.7 once other implementations caught up.

---

## Hash Lookup Step-by-Step

Given `d["key"]`:

```
1. h = hash("key")           # integer fingerprint
2. i = h % len(table)        # initial slot index
3. slot = table[i]

4. if slot is EMPTY:
       raise KeyError         # no entry, stop

5. if slot.hash == h and slot.key == "key":
       return slot.value      # found

6. else:
       i = (5*i + 1 + h) % len(table)   # pseudo-random probe
       goto step 3
```

Step 6 is the collision resolution. Python's probe sequence is derived from
the hash bits themselves — not linear scan — so collisions spread out rather
than cluster. After ~3 probes on average the key is found (at 2/3 load).

---

## The __hash__ / __eq__ Contract

**The rule:**
```
a == b  →  hash(a) == hash(b)   # MUST hold
hash(a) == hash(b)  ↛  a == b   # collisions allowed
```

**Why the rule matters:**
When Python looks up `d[key]`, it first checks hash equality (cheap, integer compare),
then key equality (potentially expensive). If the contract is broken — equal objects
have different hashes — then equal keys won't find each other's values. The dict
silently becomes wrong.

**Python's automatic enforcement:**
Defining `__eq__` without `__hash__` → Python sets `__hash__ = None`.
The class becomes unhashable. This is *not* a warning — it silently breaks things.

```python
class Broken:
    def __eq__(self, other): return True
    # __hash__ implicitly becomes None

hash(Broken())  # TypeError: unhashable type: 'Broken'
```

**Correct implementation pattern:**
```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        # hash() the same tuple you use in __eq__
        # hash(tuple) is stable, well-distributed, correct
        return hash((self.x, self.y))
```

Never use `id(self)` for `__hash__` when you also define `__eq__` —
that gives each instance a unique hash, so equal objects would still
be treated as different dict keys.

---

## Dict Views are Live

`d.keys()`, `d.values()`, `d.items()` return *view* objects, not snapshots.

```python
d = {"a": 1, "b": 2}
k = d.keys()       # view object — no copy
d["c"] = 3
print(k)           # dict_keys(['a', 'b', 'c']) — reflects the change
```

This matters for:
- Large dicts: no copy overhead when you just need to check membership
- Concurrent iteration danger: mutating while iterating a view raises RuntimeError
- Set operations: `d.keys() & other.keys()` works because keys are unique + hashable

---

## defaultdict vs setdefault vs __missing__

They solve the same problem differently. The difference matters for readability and intent.

**setdefault** — good for building nested structures inline:
```python
index = {}
for word in words:
    for ch in word:
        index.setdefault(ch, []).append(word)
# One lookup. If 'ch' not in index, inserts [] and returns it.
# If 'ch' in index, returns existing list.
```

**defaultdict** — good when all accesses to missing keys should produce the default:
```python
dd = defaultdict(list)
dd["a"].append(1)   # no check needed — "a" auto-created as []
```
Tradeoff: accessing any missing key *creates* it. Use `.get()` when you want to check without creating.

**`__missing__`** — good for custom dict subclasses with special lookup logic:
```python
class CaseDict(dict):
    def __missing__(self, key):
        if isinstance(key, str):
            lower = key.lower()
            if lower in self:
                return self[lower]
        raise KeyError(key)
```
Critical: `__missing__` is only called by `__getitem__` (`d[key]`).
`d.get(key)`, `key in d`, `d.update()` — none of these trigger `__missing__`.

---

## Counter Internals

`Counter` is a `dict` subclass. Its values are counts (integers).

```python
c = Counter("aabbc")  # {'a': 2, 'b': 2, 'c': 1}
```

Key behaviors that go beyond a plain dict:
- `c["missing_key"]` returns 0 (not KeyError) — via `__missing__`
- `most_common(n)` uses `heapq.nlargest` — O(n log k) instead of O(n log n) full sort
- Arithmetic: `c1 + c2` sums counts; `c1 - c2` drops negatives; `c1 & c2` = min; `c1 | c2` = max

When to use `Counter` vs `defaultdict(int)`:
- Need `most_common()`, arithmetic, or `subtract()` → Counter
- Just need a counter that starts at 0 → either works, defaultdict is slightly faster for pure counting

---

## ChainMap: No-Copy Namespace Stacking

`ChainMap` holds a list of mappings. Lookups search them in order. No data is copied.

```python
defaults  = {"timeout": 30, "color": "blue"}
user      = {"color": "green"}
session   = {"timeout": 60}

cfg = ChainMap(session, user, defaults)
cfg["color"]    # "green" — found in user before defaults
cfg["timeout"]  # 60 — found in session
```

Writes and deletes go to the *first* map only. This is the right model for:
- CLI args > env vars > config file > defaults (Python's own `os.environ` uses similar logic)
- Implementing scoped namespaces (Python's own `locals()`/`globals()` chain)
- Template context stacking

`new_child()` creates a new ChainMap with an empty dict prepended — efficient child scope:
```python
child = cfg.new_child({"timeout": 1})  # child scope shadows timeout
child["color"]   # still "green" from parent chain
```

---

## OrderedDict — Still Relevant in 3.12?

Plain dicts preserve insertion order since 3.7. OrderedDict still has two
capabilities plain dict lacks:

1. **`move_to_end(key, last=True/False)`** — O(1) reorder (backed by a doubly-linked list)
2. **Order-aware equality** — `OrderedDict(a=1, b=2) != OrderedDict(b=2, a=1)`

Use OrderedDict when:
- You need `move_to_end()` (e.g., an LRU cache without `functools.lru_cache`)
- You're writing code where dict equality *semantics* should be order-sensitive

---

## Key Vocabulary

| Term | Definition |
|------|-----------|
| hash table | Data structure mapping keys to values via a hash function + index array |
| load factor | Ratio of filled slots to total slots. Python resizes at ~2/3 |
| hash collision | Two different keys produce the same initial slot index |
| open addressing | Collision resolution by probing nearby slots (Python's approach) |
| compact dict | Python 3.6+ layout: sparse index array + dense entries array |
| dict view | Live view of keys/values/items — reflects mutations, no copy |
| frozenset | Immutable, hashable version of set — can be a dict key |
| `__missing__` | Hook called by `__getitem__` when a key is absent |
| hash randomization | PYTHONHASHSEED: randomizes str/bytes hash per process (security) |
