# Chapter 1 — Pitfalls: The Python Data Model

## Pitfall 1: Raising `NotImplementedError` Instead of Returning `NotImplemented`

### The Mistake
```python
class Vector:
    def __add__(self, other):
        if not isinstance(other, Vector):
            raise NotImplementedError("Can only add Vector to Vector")  # ❌ WRONG
        return Vector(self.x + other.x, self.y + other.y)
```

### Why It's Wrong
Raising `NotImplementedError` immediately kills the operation. Python never gets to try the **reflected operation** (`other.__radd__(self)`). This means you break interoperability with types that might know how to add your object.

### The Fix
```python
class Vector:
    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented  # ✅ CORRECT: a sentinel, not an exception
        return Vector(self.x + other.x, self.y + other.y)
```

Python's dispatch for `a + b`:
1. Try `a.__add__(b)` → if it returns `NotImplemented`, continue
2. Try `b.__radd__(a)` → if it returns `NotImplemented`, raise `TypeError`

---

## Pitfall 2: Forgetting `__hash__` When Defining `__eq__`

### The Mistake
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # defined
        return (self.x, self.y) == (other.x, other.y)
    # __hash__ NOT defined → Python sets it to None!

p = Point(1, 2)
{p}  # ❌ TypeError: unhashable type: 'Point'
```

### Why It Happens
When you define `__eq__`, Python automatically sets `__hash__ = None`, making the object unhashable. This is intentional: if two objects are equal, they must have the same hash. Without `__hash__`, Python can't guarantee that invariant.

### The Fix
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):  # ✅ hash same fields as __eq__
        return hash((self.x, self.y))
```

**Rule**: Hash the same fields you compare in `__eq__`. If `__eq__` uses (x, y), `__hash__` must use (x, y).

---

## Pitfall 3: `__repr__` That Can't Reconstruct the Object

### The Mistake
```python
class Config:
    def __repr__(self):
        return f"<Config object at {id(self)}>"  # ❌ Useless for debugging
```

### Why It's Wrong
The purpose of `__repr__` is to give a developer an **unambiguous, reproducible** representation. The default object repr (`<Config at 0x...>`) is what you see when you haven't implemented `__repr__` — don't mimic it.

### The Fix
```python
class Config:
    def __init__(self, host: str, port: int, debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug

    def __repr__(self):
        # ✅ Can be copy-pasted to recreate the object
        return f"Config(host={self.host!r}, port={self.port!r}, debug={self.debug!r})"
```

**Tip**: Use `!r` in f-strings for field values — it calls `repr()` on them, ensuring strings are quoted.

---

## Pitfall 4: Implementing `__bool__` That Returns a Non-Boolean

### The Mistake
```python
class Counter:
    def __init__(self, count):
        self.count = count

    def __bool__(self):
        return self.count  # ❌ Returns int, not bool
```

### Why It's Risky
Python will accept any integer from `__bool__` (0 is falsy, non-zero is truthy). But this is semantically wrong and can cause issues with type checkers and code that explicitly checks `if type(result) is bool`.

### The Fix
```python
class Counter:
    def __bool__(self):
        return self.count > 0  # ✅ Explicit bool
        # OR: return bool(self.count)
```

---

## Pitfall 5: `__len__` Returning Negative Values or Non-Integers

### The Mistake
```python
class WeirdSeq:
    def __len__(self):
        return -1  # ❌ ValueError: __len__() should return >= 0
        # OR
        return 3.5  # ❌ TypeError: __len__() should return an int
```

### Why It Matters
Python enforces that `__len__` returns a **non-negative integer**. If it returns negative or float, Python raises an exception immediately.

### The Fix
```python
class WeirdSeq:
    def __len__(self):
        return max(0, self._count)  # ✅ Always non-negative int
```

---

## Pitfall 6: Mutable Objects That Are Hashable

### The Mistake
```python
class MutablePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))  # ❌ Bad! Object is mutable!

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

p = MutablePoint(1, 2)
d = {p: "value"}
p.x = 99  # Changes hash! Now p can never be found in d again.
```

### Why It's Catastrophic
If an object's hash changes while it's stored in a dict or set, it becomes **unreachable** — the dict looks in the wrong bucket for it.

### The Fix
Make hashable objects **immutable**:
```python
class ImmutablePoint:
    __slots__ = ("_x", "_y")

    def __init__(self, x, y):
        self._x = x
        self._y = y

    # No setters → effectively immutable ✅
    @property
    def x(self): return self._x
    @property
    def y(self): return self._y

    def __hash__(self): return hash((self._x, self._y))
    def __eq__(self, other): ...
```

---

## Interview Relevance

These pitfalls are **senior-level interview topics**:
- "Why can't you put a list in a set?" → mutability + no `__hash__`
- "What's the difference between `NotImplemented` and `NotImplementedError`?" → Pitfall 1
- "Why should `__repr__` be unambiguous?" → Pitfall 3
