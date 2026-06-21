# Chapter 6 — Interview Questions: Object References, Mutability, Recycling

---

## 🟢 L3

### Q1: What does `b = a` do in Python when `a` is a list?

It creates a second name (`b`) bound to the **same list object** — not a copy. Both `a` and `b` are labels on the same object. Mutating through either name affects the same list.

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)   # [1, 2, 3, 4]
```

**To copy:** `b = list(a)` (shallow) or `b = copy.deepcopy(a)` (deep).

---

### Q2: What is the difference between `==` and `is`?

- `==` compares **values** — calls `__eq__`, can be overloaded, works for all types
- `is` compares **identity** — checks if two names refer to the exact same object in memory (`id(a) == id(b)`)

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b   # True  (same values)
a is b   # False (different objects)
```

Use `is` only for: `if x is None`, `if x is sentinel_object`. Never for strings, integers, or lists.

---

### Q3: What is a shallow copy vs a deep copy?

**Shallow copy**: Creates a new outer container, but the inner objects are shared (same references).  
**Deep copy**: Creates a completely independent duplicate — every object at every level is new.

```python
import copy
original = [[1, 2], [3, 4]]
shallow  = copy.copy(original)
deep     = copy.deepcopy(original)

original[0].append(99)
print(shallow[0])   # [1, 2, 99]  ← shared inner list
print(deep[0])      # [1, 2]      ← independent
```

---

## 🟡 L4

### Q4: Explain the mutable default argument bug. Why does it happen?

Default argument values are evaluated **once**, at function definition time — not on every call. A mutable default becomes a shared object mutated across calls.

```python
def append_to(item, lst=[]):  # lst is ONE list object for all calls
    lst.append(item)
    return lst

append_to(1)   # [1]
append_to(2)   # [1, 2]  ← accumulated from previous call!
```

The fix: use `None` as default and create a fresh object inside:

```python
def append_to(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

---

### Q5: What is "call-by-sharing" and how does it affect mutable vs immutable arguments?

Python's only parameter passing mode: **each parameter becomes an alias of the argument**. The function gets a reference to the same object — not a copy.

- **Mutable argument** (list, dict): the function can mutate it in place — the caller sees the change
- **Immutable argument** (int, str, tuple): `+=` creates a new object and rebinds the local parameter — caller's object unchanged

```python
def f(a):
    a += [99]   # in-place for list

lst = [1, 2]
f(lst)
print(lst)  # [1, 2, 99]  ← caller's list was mutated!
```

---

## 🔴 L5

### Q6: How does CPython's garbage collector work? What are its two components?

**Component 1 — Reference counting**: Every object tracks how many names point to it. When the count reaches 0, the object is immediately destroyed. This handles the vast majority of objects.

**Component 2 — Cyclic GC**: Reference counting fails for cyclic references (object A references B, B references A — both have refcount > 0 but are unreachable). CPython 2.0 added a generational garbage collector that periodically finds and collects these groups. Objects are tracked in three generations; objects that survive a GC round are promoted to the next generation (checked less frequently).

Note: `__del__` is called when an object is destroyed. In CPython this is immediate when refcount=0. In PyPy/Jython, it may be delayed arbitrarily.

---

### Q7: Why is `copy.deepcopy()` significantly slower than `copy.copy()`? What does it do internally?

`deepcopy` must:
1. **Recursively traverse** the entire object graph (every attribute, every list element)
2. **Maintain a memo dict** (`{id(original): copy}`) to detect already-copied objects and handle cyclic references without infinite recursion
3. **Construct new objects** at every level — calling `__init__` or `__copy__`/`__deepcopy__` if defined

This is O(N) in the number of objects in the graph, with high constant factors due to the recursive traversal and memo dict lookups.

For a flat list of 100 integers: `copy()` is ~5x faster than `deepcopy()`.  
For a 3-level nested list: `deepcopy()` can be 50-100x slower than `copy()`.

---

## 🟣 L6

### Q8: Explain CPython string interning. When does it apply and what are the risks of relying on it?

CPython interns (deduplicates) string objects in certain conditions:
- Strings that look like valid Python identifiers (no spaces, no special chars) are typically interned at compile time
- Short strings created at runtime may or may not be interned (implementation-specific)
- You can force interning with `sys.intern(s)`

The mechanism: a global dict maps string content → canonical string object. When a new string would be identical to an interned one, the existing object is returned instead of creating a new one.

**The risk**: `s1 is s2` may be `True` for interned strings but `False` for dynamically created strings with the same content — even in the same program. This is an optimization, not a language guarantee. Code that relies on `is` for string comparison is correct by coincidence and will fail unpredictably.

---

### Q9: A tuple containing a list is not hashable — explain exactly why, connecting to both the data model and CPython implementation.

**The data model rule**: For an object to be hashable, its hash value must never change during its lifetime. This requires that the object's value is immutable.

**The tuple's case**: A tuple's value is defined as the sequence of its elements' values. If a tuple contains a mutable list, the tuple's "value" can change (the list changes), which would change what the hash should be. Since Python can't efficiently track whether the inner list has changed, it conservatively marks tuples containing mutable objects as unhashable.

**CPython's implementation**: `tuple.__hash__` is implemented in C. It checks each element's hashability by calling `PyObject_Hash()`. If any element raises `TypeError` (because it's unhashable — lists have `__hash__ = None`), the exception propagates and `hash(tuple)` fails.

```python
t = (1, [2, 3])    # tuple with a list inside
hash(t)            # TypeError: unhashable type: 'list'

# But this is fine — frozenset enforces hashable elements:
fs = frozenset([1, 2, 3])
hash(fs)           # works!
```

The practical consequence: tuples can only be dict keys or set members if they contain only hashable elements (ints, strings, other tuples of hashables, etc.).
