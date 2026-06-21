# Chapter 5 — Pitfalls: Data Class Builders

Real bugs from production code — the ones that only bite you after you've committed and deployed.

---

## Pitfall 1: Missing `__eq__` on Plain Classes (Silent Bug)

### The Mistake
```python
class Config:
    def __init__(self, host, port):
        self.host = host
        self.port = port

c1 = Config("localhost", 8080)
c2 = Config("localhost", 8080)
print(c1 == c2)  # False! Compares object identity, not values
print(c1 in [c2])  # False — lookup silently fails
```

### Why It Matters
This exact bug causes silent test failures, broken cache lookups, and incorrect deduplication. The two configs *look* identical but are different Python objects.

### The Fix
Use any of the three builders — they all generate value-based `__eq__` automatically.

```python
from dataclasses import dataclass

@dataclass
class Config:
    host: str
    port: int

Config("localhost", 8080) == Config("localhost", 8080)  # True
```

---

## Pitfall 2: The Mutable Default Trap

### The Mistake
```python
@dataclass
class Team:
    name: str
    members: list = []   # ← ValueError at class definition time (Python catches this)

# But WITHOUT @dataclass — silently broken:
class Team:
    def __init__(self, name, members=[]):   # ← shared default!
        self.name = name
        self.members = members

t1 = Team("Alpha")
t1.members.append("Alice")

t2 = Team("Beta")
print(t2.members)  # ['Alice'] — WRONG! Shared default list mutated!
```

### Why It Fails
Default argument values are evaluated **once** at function definition. Every call that uses the default gets the **same** list object. `@dataclass` catches this pattern for annotated fields and raises `ValueError`. But plain classes with mutable defaults in `__init__` still silently share state.

### The Fix
```python
from dataclasses import dataclass, field

@dataclass
class Team:
    name: str
    members: list[str] = field(default_factory=list)  # fresh list per instance
```

---

## Pitfall 3: `@dataclass` Instances Are Not Hashable by Default

### The Mistake
```python
@dataclass
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
d = {p: "origin area"}   # TypeError!
s = {p}                   # TypeError!
```

### Why It Fails
By default, `@dataclass` sets `__hash__ = None` (making instances unhashable) when `eq=True` and `frozen=False`. This is intentional: mutable objects should not be hashable because their hash could change after insertion into a set/dict.

### The Fix
```python
# Option A: frozen (immutable + hashable)
@dataclass(frozen=True)
class Point:
    x: float
    y: float

# Option B: NamedTuple (always hashable)
from typing import NamedTuple
class Point(NamedTuple):
    x: float
    y: float
```

---

## Pitfall 4: `ClassVar` Forgotten — Field Becomes an Instance Attribute

### The Mistake
```python
from dataclasses import dataclass

@dataclass
class Registry:
    name: str
    _all_instances = set()  # Intended as class variable — but no annotation!

    def __post_init__(self):
        Registry._all_instances.add(self)
```

This *works* in the simple case. But if you add a type annotation without `ClassVar`:

```python
@dataclass
class Registry:
    name: str
    _all_instances: set = set()  # ← @dataclass now treats this as an INSTANCE FIELD
    # This raises ValueError: mutable default <class 'set'> ...
    # And even if it didn't: every instance would get its own empty set — not shared!
```

### The Fix
```python
from typing import ClassVar
from dataclasses import dataclass

@dataclass
class Registry:
    name: str
    _all_instances: ClassVar[set[str]] = set()  # ClassVar → NOT an instance field

    def __post_init__(self):
        Registry._all_instances.add(self.name)
```

---

## Pitfall 5: Type Hints Are NOT Enforced at Runtime

### The Mistake
```python
from typing import NamedTuple

class Coordinate(NamedTuple):
    lat: float
    lon: float

# This runs with NO error:
c = Coordinate(lat="NOT_A_FLOAT", lon=None)
print(c.lat + 1.0)  # TypeError — but only HERE, not at construction
```

### Why It Matters
Developers new to type hints sometimes write validation logic assuming Python enforces the hints. It doesn't. The interpreter ignores them completely.

### The Fix
- For display-only validation: just run Mypy (`mypy yourfile.py`)
- For runtime enforcement: use `__post_init__` with explicit validation

```python
from dataclasses import dataclass

@dataclass
class Coordinate:
    lat: float
    lon: float

    def __post_init__(self) -> None:
        if not isinstance(self.lat, (int, float)):
            raise TypeError(f"lat must be float, got {type(self.lat).__name__}")
```

---

## Pitfall 6: `order=True` Compares by Field Declaration Order

### The Mistake
```python
from dataclasses import dataclass

@dataclass(order=True)
class Student:
    name: str
    grade: float

students = [Student("Alice", 3.9), Student("Bob", 3.8)]
students.sort()  # sorts by NAME first, not grade!
print(students)  # [Student('Alice', 3.9), Student('Bob', 3.8)] — alphabetical by name
```

### Why It Fails
`order=True` generates comparison methods that compare fields **in declaration order**. The first field (`name`) dominates the sort. If `grade` is what you want to sort by, it must come first, or you must use a `key=` function.

### The Fix
```python
# Option A: reorder fields
@dataclass(order=True)
class Student:
    grade: float  # sort key field FIRST
    name: str

# Option B: use key= function (explicit, readable)
students.sort(key=lambda s: s.grade)
```

---

## Pitfall 7: `_replace()` on NamedTuple Does NOT Validate Types

### The Mistake
```python
from typing import NamedTuple

class Config(NamedTuple):
    host: str
    port: int

c = Config("localhost", 8080)
bad = c._replace(port="not_an_int")  # No error — silently wrong type
print(bad)  # Config(host='localhost', port='not_an_int')
```

### Why It Matters
`_replace()` constructs a new instance but bypasses any type validation (since there is none at runtime). If you have validation in `__new__` or rely on type safety, `_replace()` sidesteps it.

### The Fix
For NamedTuple: write a validated factory method instead of relying on `_replace()`.

```python
class Config(NamedTuple):
    host: str
    port: int

    def with_port(self, port: int) -> "Config":
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError(f"Invalid port: {port}")
        return self._replace(port=port)
```

For `@dataclass`, use `replace()` from dataclasses + `__post_init__` validation — which WILL run on the new instance.

---

## Interview Relevance

| Pitfall | Interview question |
|---------|-------------------|
| Missing `__eq__` | "Why does `obj1 == obj2` return False even though they have the same values?" |
| Mutable default | "What's wrong with `def __init__(self, items=[])`?" |
| Not hashable | "Can you use a `@dataclass` instance as a dict key?" |
| `ClassVar` forgotten | "What happens if you annotate a set inside a `@dataclass` without `ClassVar`?" |
| Type hints at runtime | "Do type hints enforce types at runtime in Python?" |
| `order=True` field order | "Why does `@dataclass(order=True)` not sort by the field I expect?" |
