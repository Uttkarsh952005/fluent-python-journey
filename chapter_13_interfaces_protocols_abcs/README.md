# Chapter 13 — Interfaces, Protocols, and ABCs

> **Theme**: Python evolved from pure runtime Duck Typing to explicit Goose Typing (ABCs), and finally to robust Static Duck Typing (Protocols). Understanding when to use which is the hallmark of a senior Python engineer.

## What You'll Learn

| Paradigm | Concept | When to use |
|----------|---------|-------------|
| **Duck Typing** | Implicit runtime execution (`hasattr`) | General dynamic scripting, quick tooling. |
| **Goose Typing** | Explicit runtime validation (`abc.ABC`) | Building frameworks where failing fast is critical. |
| **Static Duck Typing** | Implicit static validation (`typing.Protocol`) | Modern codebases with Mypy, dependency injection. |
| **Monkey Patching** | Altering class structures at runtime | Fixing third-party libraries, test mocking. |
| **Virtual Subclasses** | `ABC.register(Class)` | Mapping legacy code into modern ABC hierarchies. |

## Key Files

- [`examples.py`](examples.py) — Side-by-side implementations of the three typing paradigms and a custom `Tombola` ABC.
- [`exercises.py`](exercises.py) — Monkey patching `__setitem__` to fix `random.shuffle()` and registering virtual subclasses.
- [`mini_project.py`](mini_project.py) — A notification plugin system demonstrating why `Protocol` is superior to inheritance for loose coupling.
- [`benchmarks.py`](benchmarks.py) — Proves that `isinstance(obj, ABC)` is ~4x slower than a simple `hasattr()` check.
- [`notes.md`](notes.md) — The differences between `NotImplemented` and `NotImplementedError`.
- [`pitfalls.md`](pitfalls.md) — The dangers of over-engineering custom ABCs and catching `NotImplementedError`.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — CPython's `__subclasshook__` and the `ABCMeta` metaclass.

## 30-Second Rules

```python
# Rule 1: Do not create custom ABCs unless you are writing a framework.
# Instead, subclass the built-in ABCs in `collections.abc`.
from collections.abc import MutableSequence
class MyList(MutableSequence): ...

# Rule 2: If you want Mypy to verify an interface WITHOUT forcing inheritance, use Protocol.
from typing import Protocol
class Renderable(Protocol):
    def render(self) -> str: ...

# Rule 3: `NotImplemented` is a singleton you RETURN. 
# `NotImplementedError` is an exception you RAISE.
class ABC:
    def method(self):
        raise NotImplementedError  # Tell the subclass they missed it!
```

*Reference: Fluent Python 2nd ed., Chapter 13 — pages 459–504*
