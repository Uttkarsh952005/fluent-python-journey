# Chapter 3 — Pitfalls: Dicts and Sets

Common mistakes with dicts and sets — the ones that cause silent bugs,
performance regressions, or confusing behavior in production code.

---

## Pitfall 1: `{}` Creates a Dict, Not an Empty Set

### The Mistake
```python
unique = {}           # ❌ This is an empty dict!
unique.add("apple")   # AttributeError: 'dict' object has no attribute 'add'

# Or worse — silent wrong type:
seen = {}
seen.add(x)  # crashes at runtime, not at definition time
```

### Why It's Easy to Miss
The `{1, 2, 3}` syntax works for non-empty sets. Python uses `{}` for the empty
dict (for historical reasons — dicts came before sets in the language). Empty sets
have no literal syntax.

### The Fix
```python
unique = set()     # ✅ Correct empty set
unique = {1, 2}    # ✅ Non-empty set literal (fine)
empty_dict = {}    # ✅ Empty dict
```

**Habit**: When you type `{}`, ask yourself: "dict or set?" Every time.

---

## Pitfall 2: Mutating a Dict While Iterating It

### The Mistake
```python
inventory = {"apples": 5, "bananas": 0, "cherries": 3}

for item in inventory:                # ❌ Iterating the dict
    if inventory[item] == 0:
        del inventory[item]           # ❌ Mutating during iteration
# RuntimeError: dictionary changed size during iteration
```

### Why It Happens
The dict's internal iteration state tracks a slot position in the hash table.
Deleting a key can shift entries (due to compaction or rehashing), making the
iterator's position invalid. Python detects this and raises immediately.

### The Fix
```python
# Option 1: iterate over a snapshot
for item in list(inventory):          # ✅ list() copies keys first
    if inventory[item] == 0:
        del inventory[item]

# Option 2: dict comprehension (cleaner for filtering)
inventory = {k: v for k, v in inventory.items() if v > 0}   # ✅

# Option 3: collect keys to delete, then delete
to_remove = [k for k, v in inventory.items() if v == 0]
for k in to_remove:
    del inventory[k]
```

---

## Pitfall 3: `defaultdict` Silently Creates Keys on Access

### The Mistake
```python
from collections import defaultdict

dd = defaultdict(list)

# Checking if a key exists — WRONG way
if dd["users"]:           # ❌ This CREATES "users": [] and then checks it
    print("has users")
# Now "users" is in dd even though we never added anything!

# Later code that checks 'users' in dd will be True — wrong!
```

### Why It's a Problem
`defaultdict.__getitem__` calls `default_factory` for any missing key — including
when you're just "looking". This is by design, but it's a footgun when you intend
to check existence without side effects.

### The Fix
```python
# Use .get() — does NOT trigger __missing__, no side effect
if dd.get("users"):           # ✅ Returns None if absent, no key created
    print("has users")

# Or use 'in' operator — also doesn't trigger __missing__
if "users" in dd:             # ✅ No side effect
    print("has users")
```

**Rule**: Use `dd[key]` only when you intentionally want the default created.
Use `dd.get(key)` or `key in dd` when you just want to check.

---

## Pitfall 4: `__missing__` Is Not Called by `.get()`

### The Mistake
```python
class FallbackDict(dict):
    def __missing__(self, key):
        return "DEFAULT"

d = FallbackDict({"a": 1})
print(d["missing"])       # "DEFAULT"  ← works, __missing__ called
print(d.get("missing"))   # None       ← SURPRISE! __missing__ NOT called
```

### Why It Happens
`dict.get()` is implemented in C and does not call `__missing__`. It returns the
default value directly. Only `dict.__getitem__` (the `d[key]` syntax) calls
`__missing__`.

The book is explicit about this: *"The default_factory of a defaultdict is only
invoked to provide default values for `__getitem__` calls."*

### The Fix
If you need `.get()` to also use your fallback, override it:
```python
class FallbackDict(dict):
    def __missing__(self, key):
        return "DEFAULT"

    def get(self, key, default=None):
        try:
            return self[key]          # ✅ Routes through __getitem__ → __missing__
        except KeyError:
            return default
```

Or subclass `collections.UserDict` — its `get()` already delegates to `__getitem__`.

---

## Pitfall 5: Using a Mutable Default in `setdefault`

### The Mistake
```python
# Misunderstanding: thinking setdefault is like a function default argument
config = {}

# The default [] is evaluated every call — this is FINE for setdefault
config.setdefault("tags", []).append("python")
config.setdefault("tags", []).append("engineering")
# ✅ Works correctly: config["tags"] = ["python", "engineering"]
```

Wait — actually `setdefault` is safe here. The real pitfall is using `.get()` instead:

```python
config = {}
# ❌ WRONG: get() returns the default but doesn't store it
tags = config.get("tags", [])
tags.append("python")            # appends to the temp list, NOT to config
print(config)                    # {} — nothing was stored!
```

### The Fix
```python
# Use setdefault when you want to store + modify:
config.setdefault("tags", []).append("python")   # ✅

# Or be explicit:
if "tags" not in config:
    config["tags"] = []
config["tags"].append("python")                  # ✅
```

---

## Pitfall 6: Broken `__hash__` Contract — Silent Data Corruption

### The Mistake
```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash(self.x)   # ❌ Only hashes x, ignores y!

p1 = Point(1, 2)
p2 = Point(1, 3)

# p1 != p2 (correct), but hash(p1) == hash(p2) (both hash to hash(1))
# This creates a guaranteed collision in any dict/set with both points
# Lookups still work but are O(n) in the worst case — silent perf regression
```

A worse variant: hashing a mutable field:
```python
p = Point(1, 2)
d = {p: "value"}
p.x = 99            # ❌ Changes the hash! p is now "lost" in d
d[p]                # KeyError — dict looks in the wrong bucket
```

### The Fix
```python
class Point:
    def __eq__(self, other):
        if not isinstance(other, Point): return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))   # ✅ Same fields as __eq__, both fields
```

**Rules**:
1. Hash the same fields you use in `__eq__` — all of them
2. Those fields must be immutable for the lifetime of the object
3. If the object might be mutated, don't make it hashable

---

## Pitfall 7: `dict.keys()` Set Operations Return a `set`, Not a `dict_keys`

### The Surprise
```python
a = {"x": 1, "y": 2}
b = {"y": 3, "z": 4}

common = a.keys() & b.keys()
print(type(common))   # <class 'set'> — NOT dict_keys!
print(common)         # {'y'}

# You lose the association with values:
# common["y"]  → AttributeError: 'set' object has no attribute '__getitem__'
```

### Why It Matters
Set operations on dict views always return plain `set` objects, not views. If you
need the associated values after the intersection, you have to rebuild:

```python
# Get shared keys AND their values from both dicts
shared_keys = a.keys() & b.keys()
from_a = {k: a[k] for k in shared_keys}   # ✅
from_b = {k: b[k] for k in shared_keys}   # ✅
```

---

## Interview Relevance

| Pitfall | Interview question it answers |
|---------|-------------------------------|
| `{}` vs `set()` | "How do you create an empty set in Python?" |
| Mutating while iterating | "What causes RuntimeError in dict iteration?" |
| `defaultdict` side effects | "What's the difference between `dd[k]` and `dd.get(k)`?" |
| `__missing__` and `.get()` | "Does `.get()` trigger `__missing__`?" |
| Hash contract | "Can you put a mutable object in a set? Why not?" |
