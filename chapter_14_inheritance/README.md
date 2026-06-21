# Chapter 14 — Inheritance: For Better or For Worse

> **Theme**: Inheritance is often misused. Subclassing built-in C types leads to silent bugs because internal calls bypass your overrides. Multiple inheritance is powerful but requires strict adherence to `super()` cooperation and the C3 Linearization algorithm.

## What You'll Learn

| Concept | Key insight |
|---------|------------|
| The Built-in Trap | `dict.update()` in C ignores your Python `__setitem__` override. |
| Safe Subclassing | Subclass `UserDict`, `UserList`, and `UserString` from `collections`. |
| Multiple Inheritance | Supported natively. MRO resolves the diamond problem. |
| MRO (C3 Linearization) | Python calculates a flat, linear hierarchy ensuring a class is never checked before its subclasses. |
| `super()` | Doesn't mean "parent." It means "the next class in the current MRO." |
| Mixins | Classes intended for composition, not standalone instantiation. |

## Key Files

- [`examples.py`](examples.py) — The `dict` vs `UserDict` trap, and tracing `super()` across an MRO diamond graph.
- [`exercises.py`](exercises.py) — Demonstration of impossible MRO linearizations (TypeErrors) and broken `super()` chains.
- [`mini_project.py`](mini_project.py) — A modular web request pipeline composed entirely of Mixins (`LoggingMixin`, `JSONValidationMixin`).
- [`benchmarks.py`](benchmarks.py) — Measures the performance penalty of `UserDict` (~15x slower for bulk writes).
- [`notes.md`](notes.md) — The rules of Mixins and how to safely navigate multiple inheritance.
- [`pitfalls.md`](pitfalls.md) — The `**kwargs` trap in cooperative multiple inheritance.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — How `super()` acts as a dynamic proxy object at the C level.

## 30-Second Rules

```python
# Rule 1: Never subclass `dict`, `list`, or `str`. Use `collections.User*`.
from collections import UserDict
class SafeConfig(UserDict): ...

# Rule 2: Always use super() in __init__, and always accept **kwargs
class MixinA:
    def __init__(self, **kwargs):
        # We don't know what class is next in the MRO! Pass kwargs along.
        super().__init__(**kwargs)

# Rule 3: Mixins come FIRST in the class signature
class ConcreteClass(MixinA, MixinB, BaseClass): ...
```

*Reference: Fluent Python 2nd ed., Chapter 14 — pages 515–548*
