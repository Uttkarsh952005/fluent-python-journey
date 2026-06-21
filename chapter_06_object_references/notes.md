# Chapter 6 — Object References, Mutability, and Recycling

## Core Mental Model

**Variables are labels, not boxes.**

```python
a = [1, 2, 3]
b = a           # b is another label on the SAME list — NOT a copy
a.append(4)
print(b)        # [1, 2, 3, 4]  ← b sees the change
```

Assignment binds a name to an object. The object exists first (RHS evaluated), then the name is attached. Multiple names can point to the same object — that's **aliasing**.

---

## Identity vs Equality

| Operator | What it checks | Can be overloaded? | Speed |
|----------|----------------|-------------------|-------|
| `==` | **Value** (calls `__eq__`) | Yes | Slower |
| `is` | **Identity** (`id()` comparison) | No | Fastest |

```python
a == b   # are the values equal?
a is b   # are they the exact same object?
```

**Use `is` only for:**
- `if x is None`
- `if x is True / False`
- Sentinel objects: `if token is END_OF_STREAM`

**Never use `is` for strings, ints, lists, or dicts** — results depend on CPython interning (an implementation detail).

---

## Relative Immutability of Tuples

Tuples are immutable — their **references** cannot change. But if a reference points to a mutable object, that object can still mutate:

```python
t = (1, 2, [30, 40])
t[-1].append(99)    # OK! The LIST changes, not the tuple's references
# t is now (1, 2, [30, 40, 99])
```

This is why tuples containing mutable objects are **not hashable**.

---

## Shallow vs Deep Copy

```python
import copy

l1 = [1, [2, 3], (4, 5)]
l2 = list(l1)        # shallow copy — same as l1[:]
l3 = copy.deepcopy(l1)

# l2: outer list is new, inner list is SHARED with l1
# l3: everything is duplicated — fully independent
```

| Operation | Outer container | Inner objects |
|-----------|----------------|---------------|
| `l2 = l1` (alias) | same | same |
| `l2 = list(l1)` or `l1[:]` | **new** | same |
| `copy.deepcopy(l1)` | **new** | **new** |

**deepcopy handles cyclic references** — it tracks already-copied objects to avoid infinite loops.

---

## Call-by-Sharing (Python's only parameter passing mode)

Function parameters are aliases of the arguments:

```python
def f(a, b):
    a += b          # for lists: in-place, mutates caller's list
    return a        # for ints/tuples: creates new object, rebinds local 'a'

lst = [1, 2]
f(lst, [3, 4])
print(lst)          # [1, 2, 3, 4] — caller's list was mutated!
```

**The rule:** A function can mutate a mutable argument. It cannot replace the argument entirely from the caller's perspective.

---

## Mutable Default Trap

```python
# BUG — default [] is ONE object shared across all calls:
def __init__(self, items=[]):
    self.items = items          # alias to the shared default!

# FIX:
def __init__(self, items=None):
    self.items = list(items) if items is not None else []
```

Default values are evaluated once at function definition. The same list object is reused for every call that doesn't pass an argument.

---

## Defensive Copying of Arguments

```python
class Safe:
    def __init__(self, data: list):
        self.data = list(data)   # own copy — caller's list is not aliased
```

Unless a method is explicitly designed to mutate a received argument, always copy mutable arguments before storing them. Violating this principle (TwilightBus pattern) is a common source of subtle bugs.

---

## del and Garbage Collection

```python
del x       # removes the NAME 'x' — does NOT necessarily destroy the object
```

The object is destroyed only when its **reference count reaches 0**. CPython uses reference counting as its primary GC algorithm. When refcount hits 0, `__del__` (if defined) is called and memory is freed immediately.

Generational GC (added in CPython 2.0) handles **cyclic references** — objects that reference each other but are unreachable from the program.

---

## Interning — CPython Tricks with Immutables

```python
s1 = "ABC"
s2 = "ABC"
s1 is s2    # True — CPython interns short strings (implementation detail!)

t = (1, 2, 3)
tuple(t) is t    # True — tuple() returns the same object if arg is already a tuple
```

**Never rely on interning.** Always use `==` for value comparison. Interning behavior is:
- Not guaranteed across Python implementations (PyPy, Jython, etc.)
- Not documented for all cases
- Subject to change between CPython versions

---

*Reference: Fluent Python 2nd ed., Chapter 6 — pages 201–223*
