# Chapter 8 — Type Hints in Functions

> **Theme**: Type hints provide statically enforceable contracts, dramatically improving developer tooling without sacrificing Python's dynamic runtime capabilities.

## What You'll Learn

| Topic | Key insight |
|-------|------------|
| Gradual Typing | Type hints are optional. Mypy checks them statically; CPython ignores them at runtime. |
| Duck vs Nominal | Python runs purely on Duck typing. Mypy enforces strict Nominal typing. |
| Consistent-with | A more flexible `subtype-of`. `Any` is consistent with everything. |
| Postel's Law | Accept abstract types (`abc.Sequence`), return concrete types (`list`). |
| Modern Syntax | Use `list[str]` and `str \| None` (Python 3.10+) instead of `List` and `Optional`. |
| `Callable` | Annotating callbacks requires `Callable[[ArgTypes], ReturnType]`. |

## Key Files

- [`examples.py`](examples.py) — Duck vs nominal typing, Postel's law, and union syntax.
- [`exercises.py`](exercises.py) — 5 exercises on ABCs, `Any` vs `object`, and immutable sequences.
- [`mini_project.py`](mini_project.py) — A Typed Command Dispatcher utilizing `Callable` and aliases.
- [`benchmarks.py`](benchmarks.py) — Measuring the runtime introspection cost of `get_type_hints`.
- [`notes.md`](notes.md) — Syntax cheat sheets and gradual typing concepts.
- [`pitfalls.md`](pitfalls.md) — Over-constraining with `list`, defaulting to `None` without `Optional`.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — PEP 585 generics, `__annotations__`, and PEP 563.

## 30-Second Rules

```python
# Rule 1: Use ABCs for parameters to maximize caller flexibility
bad = def process(data: list[str]) -> list[str]: ...
good = def process(data: abc.Iterable[str]) -> list[str]: ...

# Rule 2: If a parameter defaults to None, use Union or Optional
bad = def format(prefix: str = None): ...
good = def format(prefix: str | None = None): ...

# Rule 3: Use | for Unions (Python 3.10+)
bad = from typing import Union; x: Union[int, float]
good = x: int | float
```

*Reference: Fluent Python 2nd ed., Chapter 8 — pages 283–338*
