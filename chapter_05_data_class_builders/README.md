# Chapter 5 — Data Class Builders

> **Chapter goal**: Know exactly which data class builder to reach for and why. Understand the internals well enough to never be surprised by `__eq__`, `__hash__`, `ClassVar`, or `field()` behavior.

---

## What You'll Learn

| Section | Core concept |
|---------|-------------|
| Boilerplate problem | Why plain classes break silently without `__eq__`/`__repr__` |
| `namedtuple` | Factory, `_fields`, `_asdict`, `_make`, `_replace`, defaults |
| `typing.NamedTuple` | Class syntax, typed fields, methods, runtime vs static type checking |
| `@dataclass` | Decorator options: `frozen`, `order`, `eq`, `unsafe_hash` |
| `field()` | `default_factory`, `repr`, `compare`, `hash`, `init`, `metadata` |
| `__post_init__` | Validation, computed fields, cross-field constraints |
| `ClassVar` / `InitVar` | Class attributes vs init-only arguments |

---

## Key Files

- [`examples.py`](examples.py) — 7-part annotated walkthrough of all builders
- [`exercises.py`](exercises.py) — 5 exercises: builder comparison, validated sensor, Money value object, JSON round-trip, typed DB rows
- [`benchmarks.py`](benchmarks.py) — instantiation, memory, equality, hashing compared across all builders
- [`mini_project.py`](mini_project.py) — schema-validated config system using all three builders together
- [`notes.md`](notes.md) — deep technical reference with comparison tables and decision flowchart
- [`pitfalls.md`](pitfalls.md) — 7 common bugs
- [`interview_questions.md`](interview_questions.md) — 9 questions from L3→L6
- [`architecture_notes.md`](architecture_notes.md) — internals: how each builder generates methods

---

## The Core Mental Model

```
Three builders, one goal: eliminate record class boilerplate.

  namedtuple:    tuple subclass → immutable, hashable, zero overhead
  NamedTuple:    namedtuple + type hints + class syntax + methods
  @dataclass:    regular class + generated methods + full flexibility

  All three auto-generate: __init__, __repr__, __eq__
  None enforce type hints at runtime (only static type checkers do)
```

---

## Builder Selection — 30-Second Guide

```
Need mutable fields?          → @dataclass
Need dict/set key (hashable)? → namedtuple / NamedTuple / @dataclass(frozen=True)
Storing millions of records?  → namedtuple / NamedTuple (no __dict__ overhead)
Need validation in __init__?  → @dataclass with __post_init__
Value object (Money, Color)?  → NamedTuple (immutable, equality by value)
Quick throwaway record?       → namedtuple
```

---

## Pre-Reading Checklist

Before starting, confirm you understand:
- [ ] Why `PlainCity() == PlainCity()` is `False` without `__eq__`
- [ ] Why `class Broken: items: list = []` is a bug (shared mutable default)
- [ ] What "tuple subclass" means for memory and API compatibility

---

*Reference: Fluent Python 2nd ed., Chapter 5 — pages 163–216*
