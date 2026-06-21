# Chapter 5 — Interview Questions: Data Class Builders

> Data class questions appear at every level — from "name the three builders" to "explain how `@dataclass` generates methods at import time." Solid answers here signal Python maturity.

---

## 🟢 L3 — Junior / Entry Level

### Q1: What is a data class and what problem does it solve?

**Expected answer:**
A data class is a class whose primary purpose is holding data — a named record with fields. Python provides three builders that auto-generate the boilerplate methods every record class needs:

```python
# Without builders: manual boilerplate (error-prone):
class Point:
    def __init__(self, x, y): self.x = x; self.y = y
    def __repr__(self): return f"Point(x={self.x}, y={self.y})"
    def __eq__(self, other): return self.x == other.x and self.y == other.y
    # ... and without __eq__, equality is identity-based — a silent bug

# With @dataclass: three lines, same result:
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
```

The three builders: `collections.namedtuple`, `typing.NamedTuple`, `@dataclass`.

---

### Q2: What is the difference between `namedtuple` and `@dataclass`?

**Expected answer:**
Two main differences:

**Mutability**: `namedtuple` produces immutable instances (it's a tuple subclass). `@dataclass` produces mutable instances by default (add `frozen=True` for immutability).

**Memory/type**: `namedtuple` stores fields in a fixed tuple — no `__dict__`, minimal overhead. `@dataclass` instances have a `__dict__` like normal classes.

```python
from collections import namedtuple
from dataclasses import dataclass

Pt = namedtuple("Pt", "x y")
p = Pt(1, 2)
p.x = 99   # AttributeError — immutable

@dataclass
class PtDC:
    x: float; y: float

pd = PtDC(1, 2)
pd.x = 99  # works — mutable
```

Also: `namedtuple` is a tuple subclass, so `isinstance(p, tuple)` is `True`. `@dataclass` is a plain class.

---

### Q3: Why can't you use a mutable default value like `[]` in a `@dataclass` field?

**Expected answer:**
Because the default value would be a **single shared object** across all instances:

```python
# With plain class — silent bug:
class Team:
    def __init__(self, members=[]):   # one list, shared by all instances!
        self.members = members

t1, t2 = Team(), Team()
t1.members.append("Alice")
print(t2.members)  # ['Alice'] — WRONG!
```

`@dataclass` detects this at class definition time and raises `ValueError: mutable default for field members is not allowed: use default_factory`. The fix:

```python
from dataclasses import dataclass, field

@dataclass
class Team:
    members: list[str] = field(default_factory=list)  # fresh list per instance
```

`default_factory` is called with zero arguments each time an instance is created, producing a new list every time.

---

## 🟡 L4 — Mid-Level

### Q4: Explain `__post_init__` — what is it for and when does it run?

**Expected answer:**
`__post_init__` is a hook called by the generated `__init__` as its final step. You use it to:
1. Validate fields (raise `ValueError` for invalid combinations)
2. Compute derived fields (fields with `init=False`)
3. Run side effects (register the instance, connect to a resource)

```python
from dataclasses import dataclass, field
import math

@dataclass
class Circle:
    radius: float
    area: float = field(init=False)   # not in __init__

    def __post_init__(self) -> None:
        if self.radius <= 0:
            raise ValueError(f"radius must be positive, got {self.radius}")
        self.area = math.pi * self.radius ** 2

c = Circle(radius=5.0)
print(c.area)  # 78.54...
Circle(radius=-1)  # ValueError
```

The generated `__init__` ends with `self.__post_init__()` (if the method exists). This is plain cooperative Python — not magic.

---

### Q5: What is the difference between `ClassVar` and a regular annotated field in `@dataclass`?

**Expected answer:**
`@dataclass` inspects `__annotations__` at class creation time to find instance fields. Any annotation using `ClassVar[T]` is **excluded** from field processing — it won't appear in `__init__`, `__repr__`, or `__eq__`.

```python
from typing import ClassVar
from dataclasses import dataclass

@dataclass
class Counter:
    name: str                         # instance field → in __init__, __repr__, __eq__
    _count: ClassVar[int] = 0         # class attr → NOT a field at all
    _MAX: ClassVar[int] = 100         # class constant → NOT a field
```

Without `ClassVar`, annotating `_count: int = 0` would make `@dataclass` treat it as an instance field with default `0` — every instance would have its own `_count`, and the shared counter logic would break.

---

### Q6: When would you use `NamedTuple` over `@dataclass`?

**Expected answer:**
`NamedTuple` for **value objects** — objects whose identity is their value, not their memory address. Classic examples: `Money`, `Coordinate`, `Version`, `Color`, `DateRange`.

Key advantages of `NamedTuple` over `@dataclass` for value objects:
1. **Immutable by default** — no risk of accidental mutation
2. **Hashable** — can be used as dict key or set member without `frozen=True`
3. **Memory-efficient** — no `__dict__` (tuple-backed storage)
4. **Tuple-compatible** — works with `sorted()`, `zip()`, `*unpacking`, positional indexing
5. **Serialization** — `_asdict()` is simpler than `dataclasses.asdict()`

Use `@dataclass` when:
- You need mutable state
- You need `__post_init__` validation
- You need `order=True` (comparison operators)
- The object has significant behavior beyond being a record

---

## 🔴 L5 — Senior

### Q7: How does `@dataclass` work internally? What happens at import time?

**Expected answer:**
`@dataclass` is a class decorator that executes at **class definition time** (import time, not instantiation time). Here's the process:

1. Python evaluates the class body and populates `cls.__annotations__` with the field names and type hints.
2. The `@dataclass` decorator inspects `__annotations__`, filters out `ClassVar` and `InitVar` entries, and collects `Field` objects via `field()` calls or defaults.
3. It **generates Python function objects** (not C code) for `__init__`, `__repr__`, `__eq__`, and optionally `__lt__`/`__hash__`/`__setattr__`/`__delattr__` — and injects them into the class with `setattr(cls, '__init__', ...)`.

This is pure Python metaprogramming — no C extensions, no metaclasses. The generated `__init__` is a real Python function (you can inspect its source via `inspect.getsource`).

**Performance implication**: The generation overhead happens once at import time. Per-instance creation is fast — it's just calling a normal Python function.

```python
import inspect, dataclasses

@dataclasses.dataclass
class Point:
    x: float
    y: float

# The generated __init__ is a real inspectable function:
print(inspect.getsource(Point.__init__))
```

---

### Q8: Explain the relationship between `frozen=True`, `eq=True`, and `__hash__` in `@dataclass`.

**Expected answer:**
Python's data model requires: **if `a == b`, then `hash(a) == hash(b)`**. Mutable objects are unsafe to hash because mutation could change `hash(obj)` after insertion into a dict/set, making the object unfindable.

`@dataclass` enforces this contract:

| `eq` | `frozen` | `__hash__` behavior |
|------|----------|-------------------|
| `False` | any | `__hash__` from parent (or `object.__hash__` = id-based) |
| `True` | `False` | `__hash__ = None` → instances **unhashable** |
| `True` | `True` | `__hash__` **generated** using all fields |
| `False` | `True` | `__hash__` from parent |

The `frozen=True` + `eq=True` combination makes instances both immutable (can't mutate after creation) and hashable (safe to use as dict key / set member).

`unsafe_hash=True` forces hash generation even for mutable classes — only use this if you know what you're doing (e.g., a logically-immutable but technically-mutable class).

---

## 🟣 L6 — Staff Engineer / Internals

### Q9: Compare the memory layouts of `namedtuple` vs `@dataclass` instances. When does the choice matter?

**Expected answer:**
**namedtuple** (tuple subclass):
- Memory layout: `ob_type` pointer + `ob_size` + N value pointers
- `sys.getsizeof(namedtuple_instance)` ≈ `56 + 8 * N` bytes (for N fields)
- No `__dict__` — fields are stored as tuple slots
- All instances of the same named tuple class share the **same** field descriptor objects (`_tuplegetter`)

**@dataclass**:
- Memory layout: standard Python object header + pointer to `__dict__`
- `sys.getsizeof(dataclass_instance)` ≈ `48 bytes` (instance shell only)
- PLUS `sys.getsizeof(instance.__dict__)` ≈ `200+ bytes` (dict overhead)
- Total per instance: ~240-280 bytes vs ~72 bytes for namedtuple (5 fields)

**When it matters**:
- Data pipelines processing millions of records: namedtuple uses ~3-4x less memory
- Replacing pandas DataFrame rows with Python objects for row-level processing: namedtuple avoids `__dict__` allocation per row
- ORM result rows: many ORMs now return named tuples for this reason
- Short-lived objects (< 1000 instances): the difference is negligible

**Also relevant**: CPython's `__dict__` uses key-sharing optimization (PEP 412) where multiple instances of the same class share one copy of the key array — reducing the 200-byte overhead somewhat for `@dataclass`, but namedtuple still wins for large N.

---

*Depth note: The best answers connect to real systems — "we replaced our 2M-row result set from `@dataclass` to `NamedTuple` and cut memory by 60%" signals real engineering experience.*
