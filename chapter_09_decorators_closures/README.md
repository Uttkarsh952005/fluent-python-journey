# Chapter 9 — Decorators and Closures

> **Theme**: Decorators are metaprogramming tools that modify or enhance functions. They rely heavily on closures to maintain state.

## What You'll Learn

| Topic | Key insight |
|-------|------------|
| Import Time | Decorators execute exactly when the module is imported. |
| Closures | Functions that remember the state of the environment where they were created. |
| `nonlocal` | Required if a closure needs to *reassign* a free variable. |
| `@functools.wraps` | Copies `__name__` and `__doc__` from the decorated function to the wrapper. |
| `@lru_cache` | Memoizes function calls. Drastically speeds up recursive algorithms. |
| `@singledispatch` | Provides elegant function overloading based on the first argument's type. |

## Key Files

- [`examples.py`](examples.py) — Import execution, closures, `nonlocal`, and the standard library decorators.
- [`exercises.py`](exercises.py) — Exercises building an accumulator, a retry mechanism, and access control.
- [`mini_project.py`](mini_project.py) — A parameterized rate-limiting API decorator using sliding windows.
- [`benchmarks.py`](benchmarks.py) — Proves the significant performance gains of `@lru_cache` vs recursive overhead.
- [`notes.md`](notes.md) — Scope rules, UnboundLocalError, and decorator factory construction.
- [`pitfalls.md`](pitfalls.md) — Losing metadata without `@wraps`, and the mutable closure trap.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — CPython's `LOAD_DEREF` bytecode and `__closure__` cells.

## 30-Second Rules

```python
# Rule 1: Always use @functools.wraps
def my_decorator(func):
    @functools.wraps(func)  # <--- NEVER FORGET THIS
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# Rule 2: Use nonlocal to mutate free variables
def counter():
    count = 0
    def inc():
        nonlocal count  # <--- Required for reassignment
        count += 1
        return count
    return inc

# Rule 3: Don't write giant if/elif type checks; use @singledispatch
```

*Reference: Fluent Python 2nd ed., Chapter 9 — pages 339–380*
