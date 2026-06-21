# Chapter 18 — with, match, and else Blocks

> **Theme**: Python provides unique block-level control flow mechanics. `with` guarantees deterministic resource cleanup regardless of execution flow, and `else` on loops allows handling "not found" scenarios cleanly without flag variables.

## What You'll Learn

| Concept | Explanation |
|---------|------------|
| Context Managers | Objects implementing `__enter__` and `__exit__` to control the `with` block. |
| `@contextmanager` | A decorator that builds a context manager out of a single generator function. |
| Exception Swallowing | If `__exit__` returns `True`, Python suppresses any exceptions raised inside the `with` block. |
| `for/else` | The `else` block executes only if the loop finishes without encountering a `break`. |
| `try/else` | The `else` block executes only if the `try` block finishes without an exception. |

## Key Files

- [`examples.py`](examples.py) — Side-by-side implementations of class-based and generator-based context managers.
- [`exercises.py`](exercises.py) — The missing `finally` leak trap and the exception swallowing bug.
- [`mini_project.py`](mini_project.py) — A realistic database transaction manager that auto-commits, auto-rolls back, and securely closes connections.
- [`benchmarks.py`](benchmarks.py) — Proves that `try/except` is faster than `if/else` on the happy path, but much slower when an exception is actually thrown.
- [`notes.md`](notes.md) — The exact protocol rules for context management.
- [`pitfalls.md`](pitfalls.md) — The readability trap of `for/else` and the resource leak of missing a `finally` around a `yield`.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — How `__exit__` args map to CPython's `sys.exc_info()`.

## 30-Second Rules

```python
# Rule 1: Always put teardown code in a finally block when using @contextmanager
@contextmanager
def file_manager():
    f = open('data.txt')
    try:
        yield f
    finally: # Critical! Runs even if `yield` throws an exception.
        f.close()

# Rule 2: Do not return True from __exit__ unless you explicitly want to silence errors.
def __exit__(self, exc_type, exc_val, tb):
    return False # Let the exception bubble up to the caller

# Rule 3: Use try/else for code that should only run if the try succeeds, but shouldn't be caught by the except block.
try:
    data = risky_fetch()
except FetchError:
    handle_error()
else:
    process_data(data) # If this throws an error, the except block will NOT catch it!
```

*Reference: Fluent Python 2nd ed., Chapter 18 — pages 685–715*
