# Chapter 1 — Architecture Notes: The Python Data Model

## Why Python Chose Protocols Over Abstract Base Classes

### The Design Decision

Python could have required explicit inheritance for type interoperability:
```python
# Java-style nominal typing — NOT how Python works
class MySeq(Sequence):
    def __len__(self): ...
    def __getitem__(self, i): ...
```

Instead, Python chose **structural subtyping** (protocols). You implement the right methods and Python treats your object as the right type — no declaration needed.

### The Trade-offs

| Aspect | Protocols (Python) | ABCs / Inheritance (Java) |
|--------|-------------------|--------------------------|
| **Flexibility** | High — any class can participate | Low — must know interface upfront |
| **Discoverability** | Low — you must know what methods to implement | High — IDE shows required methods |
| **Error messages** | Late (runtime TypeError) | Early (compile-time) |
| **Backwards compat** | High — old code works with new frameworks | Low — must explicitly implement |
| **Coupling** | Loose | Tight |

Python chose flexibility and backwards compatibility because:
1. The standard library must work with code that predates it
2. Monkey-patching and dynamic behavior are first-class in Python
3. "Easier to ask forgiveness than permission" (EAFP) is idiomatic Python

### ABCs as a Complementary Layer

`collections.abc` provides ABCs that *complement* protocols:
```python
from collections.abc import Sequence

# You CAN use inheritance for type safety and mixin methods:
class MySeq(Sequence):
    def __len__(self): ...
    def __getitem__(self, i): ...
    # Gets __contains__, __iter__, __reversed__ for free as mixins!
```

The ABCs also allow **virtual registration**:
```python
Sequence.register(MyOldClass)  # Makes isinstance(obj, Sequence) → True
```
Without touching `MyOldClass` code at all. This is how Python achieves backwards compatibility.

---

## The Memory Layout Decision: __slots__

When you define a class without `__slots__`, every instance gets a `__dict__` — a Python dictionary storing all instance attributes. This costs ~200–300 bytes per instance.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
# Each Point has a __dict__: {'x': 3, 'y': 4}
# Memory: ~232 bytes per instance
```

With `__slots__`:
```python
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y
# No __dict__: x and y stored in C-level slots
# Memory: ~56 bytes per instance
```

**When to use `__slots__`:**
- When creating millions of instances (e.g., nodes in a graph, particles in a simulation)
- When you want to prevent accidental attribute creation
- When you need maximum memory efficiency

**Cost of `__slots__`:**
- Can't add new attributes at runtime
- Complicates multiple inheritance (each class must define its slots)
- No `__dict__` means some dynamic techniques (like `vars(obj)`) don't work

---

## Why `__repr__` Should Be Reconstructable

The Python convention (from the docs):
> "If at all possible, this should look like a valid Python expression that could be used to recreate an object with the same value."

This matters for:
1. **Debugging**: `print(repr(obj))` in a debugger gives you code to paste
2. **Logging**: Log entries that include object representations are more useful
3. **Testing**: `assert eval(repr(obj)) == obj` is a powerful property test

When it's impossible to be fully reconstructable (e.g., objects with file handles, network connections), the convention is `<ClassName field=value ...>` to at least show the meaningful state.

---

## The Iteration Protocol: Two Paths

Python has two iteration paths:

### Path 1: `__iter__` (Primary — Preferred)
```python
def __iter__(self):
    return some_iterator  # Must have __next__
```
If present, Python calls `iter(obj)` → `obj.__iter__()` to get an iterator.

### Path 2: `__getitem__` (Legacy — Fallback)
```python
def __getitem__(self, index: int):
    ...  # Called with 0, 1, 2, ... until IndexError
```
If `__iter__` is absent but `__getitem__` exists, Python wraps it in a synthetic iterator that calls `__getitem__(0)`, `__getitem__(1)`, etc., stopping at `IndexError`.

**Why this fallback exists**: Pre-Python 2.2, there were no iterators. Old code only had `__getitem__`. The fallback maintains backwards compatibility with decades of Python code.

**Why you should use `__iter__`**: The fallback is less efficient, requires integer-indexed access, and the iterator position can't be persisted.

---

## Operator Overloading: The Dispatch Algorithm

For `a + b`:

```
1. type(b) is a subclass of type(a)?
   → YES: try type(b).__radd__(b, a) first
   → NO: proceed to step 2

2. Try type(a).__add__(a, b)
   → Returns value? Done.
   → Returns NotImplemented? Continue.

3. Try type(b).__radd__(b, a)
   → Returns value? Done.
   → Returns NotImplemented? Raise TypeError.
```

The subclass check exists so that `Matrix` can override behavior when combined with a base `Vector`, even when `vector + matrix` is written (Matrix on the right).

This is a subtle but important design — it ensures that more-specific types win over less-specific types in arithmetic, which matches mathematical intuition.
