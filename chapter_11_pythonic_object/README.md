# Chapter 11 — A Pythonic Object

> **Theme**: To build a class that feels like a native Python object, you must integrate seamlessly with Python's core protocols (formatting, object representation, hashing) and optimize its memory layout.

## What You'll Learn

| Topic | Key insight |
|-------|------------|
| Representations | `__repr__` is for debugging (Python expression). `__str__` is for display. |
| Formatting | `__format__` enables integration with f-strings and custom format specs. |
| Hashing | To be hashable, an object must be immutable. Use `@property` getters without setters. |
| Alt Constructors | Use `@classmethod` to create objects from varying input formats (e.g., `frombytes`). |
| Name Mangling | `__var` becomes `_Class__var`. It prevents accidental subclass overrides, not deliberate hacking. |
| `__slots__` | Bypasses the per-instance `__dict__`, saving significant memory for millions of objects. |

## Key Files

- [`examples.py`](examples.py) — A practical `Vector2d` class supporting hashing, formatting, and bytes.
- [`exercises.py`](exercises.py) — Custom mini-languages for `__format__` and name-mangling tests.
- [`mini_project.py`](mini_project.py) — An implementation-focused `Color` class with hex/rgb formatting and `__slots__`.
- [`benchmarks.py`](benchmarks.py) — Explores memory reduction via `__slots__`.
- [`notes.md`](notes.md) — Reference on `@classmethod` vs `@staticmethod` and representation dunders.
- [`pitfalls.md`](pitfalls.md) — Notes on mutable hash keys and inherited `__slots__`.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — How `__slots__` works via C-level descriptors.

## 30-Second Rules

```python
# Rule 1: Always provide a __repr__ that looks like source code
def __repr__(self):
    return f"{type(self).__name__}({self.x!r}, {self.y!r})"

# Rule 2: Use classmethods for alternative constructors
@classmethod
def from_json(cls, data):
    return cls(**json.loads(data))

# Rule 3: Use __slots__ for classes with many simple instances
class Point:
    __slots__ = ('x', 'y')  # Disables __dict__, saving significant memory
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

*Reference: Fluent Python 2nd ed., Chapter 11 — pages 391–430*
