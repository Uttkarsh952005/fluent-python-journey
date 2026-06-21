# Chapter 16 — Operator Overloading

> **Theme**: Operators are just syntactic sugar for dunder methods. Understanding how Python routes `NotImplemented` through the execution engine allows you to make custom objects interact seamlessly with built-in types.

## What You'll Learn

| Operator | Dunder Method | Fallback | Rule |
|----------|--------------|----------|------|
| `a + b` | `a.__add__(b)` | `b.__radd__(a)` | Must return a new object. |
| `a * b` | `a.__mul__(b)` | `b.__rmul__(a)` | Must return a new object. |
| `a += b` | `a.__iadd__(b)` | `a = a.__add__(b)` | Must mutate and `return self`. |
| `a == b` | `a.__eq__(b)` | `b.__eq__(a)` | Return `NotImplemented` if types mismatch. |

## Key Files

- [`examples.py`](examples.py) — Demonstrating `__add__` and duck typing `__radd__` to allow `Tuple + Vector`.
- [`exercises.py`](exercises.py) — The fatal `__iadd__` trap (overwriting an object with `None`).
- [`mini_project.py`](mini_project.py) — A 3D Matrix pipeline proving professional operator overloading safely.
- [`benchmarks.py`](benchmarks.py) — Proves that relying on `__add__` for augmented assignment (`+=`) is **~3.5x slower** than implementing `__iadd__`.
- [`notes.md`](notes.md) — The operator dispatch workflow and immutability rules.
- [`pitfalls.md`](pitfalls.md) — The `NotImplementedError` crash and mutating `self` inside `__add__`.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — The CPython `PyNumberMethods` struct and type slots.

## 30-Second Rules

```python
# Rule 1: Standard operators MUST return a new object.
def __add__(self, other):
    return Vector(self.x + other.x)

# Rule 2: In-place operators MUST mutate and return self.
def __iadd__(self, other):
    self.x += other.x
    return self  # Fatal bug if forgotten!

# Rule 3: Return NotImplemented when you don't recognize the other operand.
def __mul__(self, scalar):
    if not isinstance(scalar, (int, float)):
        return NotImplemented
    return Vector(self.x * scalar)
```

*Reference: Fluent Python 2nd ed., Chapter 16 — pages 589–632*
