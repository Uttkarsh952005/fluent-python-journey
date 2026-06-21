# Chapter 11 — Pitfalls: A Pythonic Object

---

## Pitfall 1: Mutating a Hashable Object

If you implement `__hash__` and `__eq__`, your object can be stored in a `set` or used as a `dict` key. However, if the attributes used to calculate the hash change *after* the object is inserted into the dictionary, the object is effectively lost.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __hash__(self): return hash((self.x, self.y))
    def __eq__(self, other): return (self.x, self.y) == (other.x, other.y)

p = Point(1, 2)
grid = {p: "Origin"}

p.x = 99  # DANGER: Mutated after hashing!
print(grid.get(p))  # Returns None! The hash changed, so the dict looks in the wrong bucket.
```

**Fix:** If an object is hashable, its hash dependencies must be strictly immutable. Use "private" variables (`_x`) and expose them via `@property` getters without a setter.

---

## Pitfall 2: `__slots__` Are Not Inherited Easily

When a subclass inherits from a class with `__slots__`, the subclass **does not automatically enforce slots**. The subclass will still generate a `__dict__` for its own instances, completely neutralizing the memory savings.

```python
class Base:
    __slots__ = ('x', 'y')

class Child(Base):
    pass

c = Child()
c.z = 42  # Works! Because Child still has a __dict__!
```

**Fix:** You must declare `__slots__ = ()` (an empty tuple) in the subclass if it adds no new attributes, or define a new `__slots__` tuple with only the *new* attributes.

---

## Pitfall 3: `__slots__` Breaks `weakref`

Objects with `__slots__` cannot be targets of weak references (`weakref.ref()`). If a framework (like a caching system or an event dispatcher) relies on weak references to avoid memory leaks, your slotted object will crash the system.

**Fix:** If you need both memory savings and weak reference support, explicitly add `'__weakref__'` to your slots tuple.

```python
class FastPoint:
    __slots__ = ('x', 'y', '__weakref__')
```

---

## Pitfall 4: Misusing `__repr__` as `__str__`

Developers often dump complex JSON strings or unreadable debug logs into `__repr__`.

```python
class User:
    def __repr__(self):
        return f"User logged in at {self.time} with IP {self.ip} and token {self.token}"
```

**Fix:** `__repr__` should ideally evaluate to a Python expression that reconstructs the object. Reserve human-readable logs for `__str__`.

```python
class User:
    def __repr__(self):
        return f"User({self.id!r}, {self.name!r})"
```
