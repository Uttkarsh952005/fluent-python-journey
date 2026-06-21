# Chapter 17 — Iterators, Generators, and Classic Coroutines

> **Theme**: `yield` fundamentally alters how a function behaves, changing it from a standard C-stack subroutine into a suspendable, resumable coroutine. Generators enable O(1) memory processing via lazy evaluation.

## What You'll Learn

| Concept | Explanation |
|---------|------------|
| **Iterable** | An object containing data. It implements `__iter__` to return an Iterator. |
| **Iterator** | An engine that fetches data. It implements `__next__`. |
| **Generator** | A function containing `yield`. It returns an Iterator implicitly. |
| **`yield from`** | Delegates iteration strictly to a sub-generator, bridging the outer caller to the inner sub-gen. |
| **Coroutines** | Generators used to consume data via `.send(data)` instead of just producing it. |

## Key Files

- [`examples.py`](examples.py) — Demonstrates lazy evaluation, `yield from` mechanics, and a classic `.send()` coroutine.
- [`exercises.py`](exercises.py) — The Generator Exhaustion trap and the Coroutine Priming trap.
- [`mini_project.py`](mini_project.py) — A realistic data pipeline constructed entirely out of chained generators to process data exactly like Unix pipes (`|`).
- [`benchmarks.py`](benchmarks.py) — Proves via `tracemalloc` that generating 2 million items eagerly in a list costs **~17 MB** of RAM, while doing it via a lazy generator costs practically **0 MB**.
- [`notes.md`](notes.md) — The mechanical difference between Iterators and Iterables.
- [`pitfalls.md`](pitfalls.md) — The fatal mistake of returning lists inside what should be a generator.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — The CPython `YIELD_VALUE` opcode and `PyFrameObject` suspension.

## 30-Second Rules

```python
# Rule 1: A generator is strictly single-use. If you need to loop twice, create it twice.
gen = (x for x in range(10))
list(gen) # [0, 1, ..., 9]
list(gen) # [] <-- EMPTY!

# Rule 2: If a function returns a large list, refactor it to `yield`.
# BAD: O(N) memory
def get_lines(file):
    return file.readlines()

# GOOD: O(1) memory
def get_lines(file):
    for line in file:
        yield line

# Rule 3: Always prime a coroutine by calling next(coro) before sending data.
coro = my_coro()
next(coro) # Essential!
coro.send(data)
```

*Reference: Fluent Python 2nd ed., Chapter 17 — pages 625–690*
