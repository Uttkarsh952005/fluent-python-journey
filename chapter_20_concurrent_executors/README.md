# Chapter 20 — Concurrent Executors

> **Theme**: `concurrent.futures` elevates Python concurrency from raw low-level thread/process spawning into a high-level orchestration model based on `Futures`.

## What You'll Learn

| Method | Returns | Blocking Behavior | Best For |
|--------|---------|-------------------|----------|
| `executor.submit(func, args)` | A single `Future` object | Non-blocking. | Disparate tasks with varied arguments. |
| `executor.map(func, iter)` | A generator of results | Blocks until the *next* item in order is ready. | Drop-in replacement for standard `map`. |
| `futures.as_completed(futures)` | An iterator of completed `Future`s | Blocks until *any* future completes. | Progress bars, responsive UIs, logging. |
| `future.result()` | The return value of the task | Blocks until that specific task is done. | Final retrieval of data. |

## Key Files

- [`examples.py`](examples.py) — Demonstrating `map`, `submit`, and `as_completed`.
- [`exercises.py`](exercises.py) — The absolute necessity of checking `.result()` or `.exception()` to avoid silent thread failures.
- [`mini_project.py`](mini_project.py) — A live server health dashboard that yields real-time statuses as servers respond, rather than batching them.
- [`benchmarks.py`](benchmarks.py) — A Time-To-First-Result benchmark. Proves that if Task 0 takes 10s and Task 1 takes 1s, `map()` blocks you for 10s, while `as_completed()` yields Task 1 immediately.
- [`notes.md`](notes.md) — What a Future actually represents and the `__exit__` guarantees of Executors.
- [`pitfalls.md`](pitfalls.md) — The silent memory explosion trap of submitting 1 million tasks into an unbounded executor queue.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — How Python manages internal work queues and thread pooling.

## 30-Second Rules

```python
# Rule 1: Always retrieve the results of your futures to catch exceptions!
# BAD: Exception is silently swallowed.
executor.submit(flaky_task)

# GOOD: Exception will be raised and caught here.
future = executor.submit(flaky_task)
future.result() 

# Rule 2: If you want to show a progress bar (like tqdm), you MUST use as_completed.
with ThreadPoolExecutor() as ex:
    futures = [ex.submit(work, x) for x in range(100)]
    for f in tqdm(as_completed(futures)):
        result = f.result()
```

*Reference: Fluent Python 2nd ed., Chapter 20 — pages 765–810*
