# Chapter 12 — Special Methods for Sequences

> **Theme**: To make a custom class feel like a native Python sequence, you do not need to inherit from anything. You just need to implement the sequence protocol (`__len__` and `__getitem__`) and handle slice objects correctly.

## What You'll Learn

| Topic | Key insight |
|-------|------------|
| Sequence Protocol | Python asks "does it have `__len__` and `__getitem__`?" instead of "is it a `Sequence`?" |
| `slice` Objects | `my_obj[1:4]` passes a `slice(1, 4, None)` object to `__getitem__`. |
| Slice Awareness | A slice of a custom class should return a new instance of that class, not a native list. |
| `__getattr__` | Intercepts attribute lookups *only* when the attribute is not found in `__dict__`. |
| Shadowing | If you don't restrict `__setattr__`, users can assign `obj.x = 10`, silencing your `__getattr__` logic permanently. |
| Hashing N-Dimensions | Combine `map(hash, components)` with `functools.reduce(operator.xor, ...)` for fast, reliable hashing. |
| Short-circuit `__eq__` | Avoid converting large arrays to tuples just to compare them. Use `zip()` and `all()`. |

## Key Files

- [`examples.py`](examples.py) — The multidimensional `Vector` implementing sequence protocols and dynamic properties.
- [`exercises.py`](exercises.py) — Proving duck-typing fallbacks (like `reversed()`) and catching the `__getattr__` recursion bug.
- [`mini_project.py`](mini_project.py) — A `TimeSeries` sequence mapping `.max` and `.min` via `__getattr__`.
- [`benchmarks.py`](benchmarks.py) — Demonstrates that short-circuit `__eq__` is significantly faster than tuple conversion.
- [`notes.md`](notes.md) — Reference on duck typing, slicing, and hashing multidimensional objects.
- [`pitfalls.md`](pitfalls.md) — Infinite recursion in `__getattr__` and returning native arrays from slices.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — How Python implements `slice` objects internally.

## 30-Second Rules

```python
# Rule 1: Always check for slice objects in __getitem__
def __getitem__(self, index):
    if isinstance(index, slice):
        return type(self)(self._data[index])  # Return a new instance!
    return self._data[index]

# Rule 2: If you implement __getattr__, heavily restrict __setattr__
def __setattr__(self, name, value):
    if name in self.dynamic_fields:
        raise AttributeError(f"Read-only attribute {name}")
    super().__setattr__(name, value)

# Rule 3: Use zip() and all() for fast sequence equality
def __eq__(self, other):
    return len(self) == len(other) and all(a == b for a, b in zip(self, other))
```

*Reference: Fluent Python 2nd ed., Chapter 12 — pages 425–461*
