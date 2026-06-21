# Chapter 5 — Data Class Builders

## Chapter Goal

Understand the three data class builders Python provides, when to use each, and how they work internally — so you can make deliberate design choices instead of defaulting to `@dataclass` for everything.

---

## The Three Builders at a Glance

| Feature | `namedtuple` | `NamedTuple` | `@dataclass` |
|---------|-------------|-------------|-------------|
| Available since | Python 2.6 | Python 3.5 | Python 3.7 |
| Class syntax | ✗ | ✓ | ✓ |
| Type annotations | ✗ | ✓ | ✓ |
| Mutable instances | ✗ | ✗ | ✓ (default) |
| Tuple subclass | ✓ | ✓ | ✗ |
| `__hash__` | ✓ (inherited) | ✓ (inherited) | ✗ (unless `frozen=True`) |
| `order=True` available | ✗ | ✗ | ✓ |
| `__post_init__` | ✗ | ✗ | ✓ |
| Memory per instance | Minimal (no `__dict__`) | Minimal | Higher (has `__dict__`) |
| Field defaults | rightmost only | rightmost only | all positions |
| Conversion to dict | `._asdict()` | `._asdict()` | `asdict()` |
| New instance with changes | `._replace()` | `._replace()` | `replace()` |

---

## The Boilerplate Problem

Without data class builders, a record class requires:
- `__init__`: one line per field × 3 (parameter, assignment, `self.x = x`)
- `__repr__`: manual formatting
- `__eq__`: manual field comparison

Miss `__eq__` and two "identical" instances compare as unequal (comparing object IDs, not values). This is a silent bug.

All three builders auto-generate `__init__`, `__repr__`, `__eq__`. That's the core value.

---

## `collections.namedtuple` — The Original

```python
from collections import namedtuple

City = namedtuple("City", "name country population")
tokyo = City("Tokyo", "JP", 37.4)

# Tuple-compatible:
tokyo[0]           # "Tokyo" — index access
tokyo._asdict()    # {'name': 'Tokyo', 'country': 'JP', 'population': 37.4}
City._make(row)    # construct from any iterable
tokyo._replace(population=37.5)  # new tuple with one field changed

# Defaults (rightmost N fields only):
Coord = namedtuple("Coord", "lat lon ref", defaults=["WGS84"])
Coord(0, 0)  # Coord(lat=0, lon=0, ref='WGS84')
```

**Best for**: CSV rows, DB result sets, any large read-only record collection. Zero memory overhead vs plain tuple.

---

## `typing.NamedTuple` — Typed + Methods

```python
from typing import NamedTuple

class Coordinate(NamedTuple):
    lat: float
    lon: float
    reference: str = "WGS84"  # default for rightmost fields

    def __str__(self) -> str:
        ns = "N" if self.lat >= 0 else "S"
        return f"{abs(self.lat):.1f}°{ns}"
```

Same memory efficiency as `namedtuple`. Adds type annotations (enforced by type checkers, NOT at runtime) and natural class syntax for methods.

**Best for**: value objects — `Money`, `Coordinate`, `Color`, `Version`. Immutable, hashable, equality by value.

---

## `@dataclass` — The Modern Workhorse

```python
from dataclasses import dataclass, field

@dataclass(frozen=False, order=False, eq=True)
class ClubMember:
    name: str
    guests: list[str] = field(default_factory=list)
    athlete: bool     = field(default=False, repr=False)
```

Key `@dataclass` parameters:

| Param | Default | Effect |
|-------|---------|--------|
| `init` | `True` | Generate `__init__` |
| `repr` | `True` | Generate `__repr__` |
| `eq` | `True` | Generate `__eq__` |
| `order` | `False` | Generate `__lt__`, `__le__`, `__gt__`, `__ge__` |
| `frozen` | `False` | Raise `FrozenInstanceError` on mutation |
| `unsafe_hash` | `False` | Force `__hash__` even if mutable |

**Best for**: mutable entities, objects with business logic, anything needing `__post_init__`.

---

## `field()` Reference

```python
from dataclasses import field

@dataclass
class Example:
    name: str
    items: list[str]  = field(default_factory=list)   # fresh list per instance
    _internal: str    = field(default="", repr=False)  # hidden from repr
    sort_key: float   = field(default=0.0, compare=False)  # excluded from __eq__
    created: date     = field(default=None, hash=False)    # excluded from __hash__
    metadata: dict    = field(default=None, init=False)    # not in __init__ at all
```

**The mutable default trap**: `field: list = []` raises `ValueError` at class definition time. Always use `field(default_factory=list)`.

---

## `__post_init__` — Validation and Computed Fields

```python
@dataclass
class Circle:
    radius: float
    area: float = field(init=False)  # not in __init__

    def __post_init__(self) -> None:
        import math
        if self.radius <= 0:
            raise ValueError(f"radius must be positive, got {self.radius}")
        self.area = math.pi * self.radius ** 2
```

Runs as the final step of the generated `__init__`. Use for:
- Field validation (cross-field constraints)
- Computed fields (`init=False`)
- Side effects (registry, logging)

---

## `ClassVar` vs Instance Fields

```python
from typing import ClassVar

@dataclass
class Tracker:
    name: str
    _count: ClassVar[int] = 0   # NOT an instance field — @dataclass ignores it

    def __post_init__(self):
        Tracker._count += 1
```

Without `ClassVar`: @dataclass would treat `_count` as an instance field and include it in `__init__`, `__repr__`, and `__eq__`. With `ClassVar`: it becomes a transparent class attribute.

---

## `InitVar` — Init-Only Arguments

```python
from dataclasses import InitVar

@dataclass
class Config:
    host: str
    port: int
    raw_dict: InitVar[dict | None] = None   # NOT stored, passed to __post_init__

    def __post_init__(self, raw_dict: dict | None) -> None:
        if raw_dict:
            self.host = raw_dict.get("host", self.host)
            self.port = raw_dict.get("port", self.port)
```

`InitVar` fields appear in `__init__` but are NOT stored as instance attributes.

---

## Decision Flowchart

```
Do you need mutable instances?
  YES → @dataclass (with or without frozen=True)
  NO  →
    Do you need type annotations?
      YES → typing.NamedTuple (class syntax, methods, typed)
      NO  → collections.namedtuple (simple, minimal)

Do you need it hashable (dict key / set member)?
  namedtuple / NamedTuple → always hashable
  @dataclass → only if frozen=True (or unsafe_hash=True)

Are you storing millions of instances?
  YES → namedtuple / NamedTuple (no __dict__ overhead)
  NO  → doesn't matter
```

---

## Type Hints — No Runtime Effect

```python
class Coordinate(NamedTuple):
    lat: float
    lon: float

# This runs fine — type hints NOT enforced at runtime:
Coordinate(lat="wrong", lon=None)  # No error!
```

Type hints are documentation verified by static checkers (Mypy, Pyright). The Python interpreter ignores them completely. Never write runtime validation logic that assumes type hints are enforced.

---

*Reference: Fluent Python 2nd ed., Chapter 5 — pages 163–216*
