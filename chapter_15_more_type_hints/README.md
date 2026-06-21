# Chapter 15 — More About Type Hints

> **Theme**: Advanced static typing in Python requires understanding the boundary between Mypy and the CPython runtime. Tools like `@overload`, `TypedDict`, and `cast()` are pure static constructs — they literally vanish when your code executes.

## What You'll Learn

| Concept | Key insight |
|---------|------------|
| `@overload` | Defines multiple function signatures for Mypy. The bodies are ignored at runtime. |
| `TypedDict` | Enforces specific keys and types on a dictionary. Has exactly zero runtime overhead. |
| `typing.cast()` | Overrides Mypy's inference. Dangerous because it provides no runtime validation. |
| Generics (`TypeVar`) | Links the input type of a function directly to its output type. |
| `Any` vs `object` | `Any` turns the type checker off. `object` is the strict root of the class hierarchy. |

## Key Files

- [`examples.py`](examples.py) — Implementing `@overload` chains and mapping untyped data via `cast()` and `TypedDict`.
- [`exercises.py`](exercises.py) — Proving that Python throws away the logic inside `@overload` bodies.
- [`mini_project.py`](mini_project.py) — A realistic JSON API pipeline crossing the dynamic/static boundary safely.
- [`benchmarks.py`](benchmarks.py) — Proves that `TypedDict` instantiates exactly as fast as a raw dict, making it ~3x faster than `@dataclass`.
- [`notes.md`](notes.md) — The mechanical differences between `TypedDict` and `dataclass`.
- [`pitfalls.md`](pitfalls.md) — The fatal assumption that `cast` performs runtime validation, and the `@overload` logic trap.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — The `typing.py` source code for `cast()`.

## 30-Second Rules

```python
# Rule 1: Don't put logic in @overloads. It will be thrown away.
@overload
def process(x: int) -> int: ... # Note the `...` body

# Rule 2: Use TypedDict for JSON, use dataclass for internal Objects
class JSONPayload(TypedDict):
    id: int  # Zero runtime overhead, pure dictionary speed.

# Rule 3: Use cast() sparingly, as it lies to the type checker.
from typing import cast
typed_data = cast(JSONPayload, json.loads(raw_data))
```

*Reference: Fluent Python 2nd ed., Chapter 15 — pages 547–594*
