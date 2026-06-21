# Chapter 5 — Architecture Notes: Data Class Builders

How each builder generates its methods, why the designs differ, and what the design decisions reveal about Python's metaprogramming model.

---

## How `collections.namedtuple` Works

`namedtuple` is a **class factory** — a function that dynamically creates and returns a new class. Its implementation (in `collections/__init__.py`) works by:

1. Validating field names (no duplicates, no Python keywords, no leading underscores unless `rename=True`)
2. Building a Python source string for the class — `__new__`, `__repr__`, `__getnewargs__`, etc.
3. `exec()`-ing that source string in a fresh namespace
4. Returning the resulting class

This is literally code generation via string concatenation — the same technique used in early Django ORM code. You can see it yourself:

```python
from collections import namedtuple
import inspect

City = namedtuple("City", "name country population")
print(inspect.getsource(City.__new__))
# Shows the generated code string
```

**Why a factory and not a decorator?** Named tuples need to be tuple subclasses. A class decorator applied to a plain `class Foo: ...` can't retroactively make it a tuple subclass — the MRO is fixed at class creation. Creating a *new* class (via factory) is the only way.

---

## How `typing.NamedTuple` Works

`typing.NamedTuple` uses Python's **metaclass protocol** to intercept the class creation process. When you write:

```python
class Coordinate(NamedTuple):
    lat: float
    lon: float
```

Python calls `type.__prepare__()` to create the class namespace, then calls `type.__new__()`. The `NamedTuple` metaclass intercepts `__new__`, reads the `__annotations__` dict, and calls `collections.namedtuple()` internally to create a proper named tuple class — then returns that instead of the plain class.

**The result**: `Coordinate` is a `namedtuple`-generated class, not a subclass of `NamedTuple`. That's why:

```python
issubclass(Coordinate, tuple)         # True  — it IS a tuple subclass
issubclass(Coordinate, NamedTuple)    # False — NamedTuple was just the syntax vehicle
```

`NamedTuple` is not in the MRO at all. It's a metaclass trick.

---

## How `@dataclass` Works

`@dataclass` is a **class decorator** — it receives a completed class and modifies it in place. The process:

1. **Inspect annotations**: reads `cls.__annotations__`, filters `ClassVar` and `InitVar` entries
2. **Build Field objects**: for each non-ClassVar annotation, create a `Field` descriptor with default, metadata, etc.
3. **Generate `__init__`**: construct a function source string, `exec()` it, and inject via `setattr(cls, '__init__', ...)`
4. **Generate other methods**: same process for `__repr__`, `__eq__`, `__lt__` (if `order=True`), `__hash__`, `__setattr__`/`__delattr__` (if `frozen=True`)

The generated `__init__` is a real Python function — you can call `inspect.getsource()` on it. This is different from `namedtuple` which returns a *new* class; `@dataclass` modifies the *existing* class.

**Why exec() and not `types.FunctionType`?** The generated functions need to reference field defaults by name in their closures. Building function objects directly from bytecode would require knowing CPython's bytecode format. Building source strings is simpler and works across CPython, PyPy, etc.

---

## The `__annotations__` Protocol

All three builders rely on Python's `__annotations__` mechanism (PEP 526). When Python processes a class body, any `name: type` annotation becomes an entry in `cls.__annotations__`. If a value is also assigned (`name: type = value`), that value becomes a class attribute.

```python
class Demo:
    a: int           # only in __annotations__; no class attribute 'a'
    b: float = 1.1   # in __annotations__ AND as class attribute b = 1.1
    c = "spam"       # NOT in __annotations__; plain class attribute

Demo.__annotations__  # {'a': <class 'int'>, 'b': <class 'float'>}
Demo.a                # AttributeError — annotation only, no value bound
Demo.b                # 1.1
Demo.c                # 'spam'
```

`@dataclass` exploits this:
- Fields with annotations → instance attributes (generated in `__init__`)
- `ClassVar[T]` annotations → class attributes (skipped by @dataclass)
- Unannotated class attributes (`c = "spam"`) → untouched class attributes

---

## The `frozen=True` Implementation

`frozen=True` doesn't actually make the object immutable at the C level. Instead, `@dataclass` generates `__setattr__` and `__delattr__` methods that raise `FrozenInstanceError` (a subclass of `AttributeError`).

```python
# What @dataclass generates for frozen=True:
def __setattr__(self, name, value):
    raise dataclasses.FrozenInstanceError('cannot assign to field ' + repr(name))

def __delattr__(self, name):
    raise dataclasses.FrozenInstanceError('cannot delete field ' + repr(name))
```

**The bypass**: you can still mutate via `object.__setattr__(instance, 'field', value)` — which bypasses the generated `__setattr__`. This is why Ramalho says instances will be "reasonably safe from accidental change, but not really immutable." A determined programmer can always circumvent it.

**Why not use `__slots__` with no setters?** `__slots__` without `__dict__` would be truly immutable at the C level, but `@dataclass` would lose the flexibility to work with existing classes that might already define `__dict__`. `__slots__` and `@dataclass` can be combined manually but aren't automatic.

---

## `namedtuple` Memory Model vs `@dataclass`

```
namedtuple instance (5 fields):
┌───────────────────────────────┐
│ ob_refcnt    (8 bytes)        │
│ ob_type ptr  (8 bytes)        │
│ ob_size      (8 bytes)        │
│ item[0] ptr  (8 bytes)  ←── "Tokyo"   │
│ item[1] ptr  (8 bytes)  ←── "JP"      │
│ item[2] ptr  (8 bytes)  ←── 37.4      │
│ item[3] ptr  (8 bytes)  ←── 35.68     │
│ item[4] ptr  (8 bytes)  ←── 139.69    │
└───────────────────────────────┘
Total: ~72 bytes + the referenced objects

@dataclass instance (5 fields):
┌───────────────────────────────┐
│ ob_refcnt    (8 bytes)        │
│ ob_type ptr  (8 bytes)        │
│ __dict__ ptr (8 bytes)  ──→  ┌──────────────────────────────┐
└───────────────────────────────┘  │ dict header (56+ bytes)      │
                                   │ "name" → ptr → "Tokyo"       │
                                   │ "country" → ptr → "JP"       │
                                   │ "population" → ptr → 37.4    │
                                   │ "lat" → ptr → 35.68          │
                                   │ "lon" → ptr → 139.69         │
                                   └──────────────────────────────┘
Total: ~48 bytes (shell) + ~200+ bytes (__dict__) = ~248+ bytes
```

**PEP 412 key sharing** (Python 3.3+) reduces `__dict__` overhead by sharing the key array across instances of the same class, but the values array is still per-instance. For large N, namedtuple still wins by 3-4x.

---

## The "Data Class as Code Smell" Argument

The chapter's epigraph (Martin Fowler and Kent Beck) is deliberate: data classes are a code smell when they're *only* data with no behavior. Pure data classes invite "feature envy" — other classes accessing their fields directly and performing operations that should be methods of the data class.

The progression:
1. Start with `@dataclass` for a quick record
2. Add `__post_init__` for validation
3. Add methods for domain operations
4. Realize it's become a real class — consider whether the builder is still needed

The builders are starting points, not permanent solutions. Ramalho's point: it's fine to graduate a `@dataclass` into a full class with `__init__` written by hand if the class has grown complex enough to justify it.

---

## Why `NamedTuple` Uses Metaclass, Not Decorator

A class decorator (like `@dataclass`) receives a fully-constructed class and modifies it. But by the time the decorator runs, the class hierarchy (`__bases__`) is already fixed. Making a class a `tuple` subclass *after* construction is impossible.

`NamedTuple` uses a metaclass to intercept the class creation *before* the class object is built — at `type.__new__()` time. This allows it to substitute a `namedtuple`-generated class for the plain class, giving the result the correct `tuple` MRO.

This is one of the rare legitimate uses of metaclasses: when you need to change the fundamental type of the resulting class object, not just modify it after the fact.
