# Chapter 24 — Class Metaprogramming

> **Theme**: Code that writes code. By hijacking the class creation sequence via `__init_subclass__` or Metaclasses, you can build declarative frameworks (like Django, Pydantic, or SQLAlchemy) that automatically register plugins, validate methods, and inject dependencies.

## What You'll Learn

| Concept | Explanation |
|---------|------------|
| **Evaluation Time** | When Python reads a file top-to-bottom and builds the class definitions. Metaprogramming happens here. |
| **Class Decorator** | Wraps a class *after* it has been fully built. Easy to write, limited scope. |
| `__init_subclass__` | Placed in a base class, it automatically triggers whenever a subclass is created. Safe, modern, and covers 90% of use cases. |
| **Metaclass** | A class that inherits from `type` and intercepts the raw dictionary of variables *before* the class physically exists. |

## Key Files

- [`examples.py`](examples.py) — Demonstrating the three tiers of metaprogramming: Class Decorators, `__init_subclass__` for plugin registries, and a raw Metaclass for enforcing method capitalization rules.
- [`exercises.py`](exercises.py) — The Execution Timeline exercise. Proves with `print` statements that the class body evaluates completely independently of `main()` execution.
- [`mini_project.py`](mini_project.py) — A simulated Dependency Injection framework. The Metaclass intercepts the class build process to automatically inject database and logger attributes into service classes, keeping business logic pristine.
- [`benchmarks.py`](benchmarks.py) — Proves that while Metaclasses do heavy lifting, they cost *zero* CPU overhead at runtime, because all metaprogramming executes at import time.
- [`notes.md`](notes.md) — What a metaclass is (`type(int) -> type`).
- [`pitfalls.md`](pitfalls.md) — The Metaclass Conflict (inheriting from two metaclasses causes a crash) and the Golden Rule of Metaclasses.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — The fundamental Python class creation sequence.

## 30-Second Rules

```python
# Rule 1: Default to __init_subclass__. It avoids Metaclass Conflicts.
class Registry:
    plugins = []
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.plugins.append(cls)

# Rule 2: If you must use a Metaclass, it MUST inherit from type.
class StrictMeta(type):
    def __new__(meta, name, bases, dic):
        return super().__new__(meta, name, bases, dic)

# Rule 3: Metaprogramming executes at IMPORT time. 
# Do not put database queries inside a Metaclass __new__ method unless you want 
# your server to crash before `main()` even runs!
```

*Reference: Fluent Python 2nd ed., Chapter 24 — pages 939–985*
