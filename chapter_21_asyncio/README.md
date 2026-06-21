# Chapter 21 — Asynchronous Programming

> **Theme**: Modern Python concurrency relies on an Event Loop. By explicitly writing `await`, you cooperatively hand control of the single execution thread back to the orchestrator, eliminating race conditions while scaling to millions of I/O operations.

## What You'll Learn

| Concept | Explanation |
|---------|------------|
| **Event Loop** | The single-threaded engine that schedules and runs asynchronous tasks. |
| **Coroutine** | A function defined with `async def`. It does not execute until awaited. |
| **`await`** | The keyword that pauses a coroutine and yields control back to the loop. |
| **`asyncio.gather`** | Executes multiple awaitables concurrently, preserving order. |
| **`asyncio.Semaphore`** | A critical lock used to limit how many coroutines can access a resource at once. |

## Key Files

- [`examples.py`](examples.py) — Native coroutines, `gather`, and responsive `as_completed` loops.
- [`exercises.py`](exercises.py) — The fatal Blocking Trap (proving that `time.sleep` freezes the entire application).
- [`mini_project.py`](mini_project.py) — A high-speed web scraper architected with `asyncio.Semaphore` to throttle concurrency and prevent "Too Many Open Files" OS crashes.
- [`benchmarks.py`](benchmarks.py) — Proves that `asyncio.to_thread()` is strictly required when running legacy synchronous code (like `requests.get()`) inside an async application.
- [`notes.md`](notes.md) — Clarifying the terminology: Awaitables, Coroutines, and Tasks.
- [`pitfalls.md`](pitfalls.md) — Forgetting to await, missing semaphores, and blocking the loop.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — How the Event Loop relies on the OS `selectors` module (`epoll`/`kqueue`).

## 30-Second Rules

```python
# Rule 1: NEVER use blocking synchronous libraries (like requests) in async code.
# Use aiohttp or httpx.AsyncClient instead.
async def get_data():
    requests.get("...") # FATAL! Freezes the whole server.

# Rule 2: If you MUST use a blocking library, wrap it in to_thread.
async def get_data_safe():
    await asyncio.to_thread(requests.get, "...") # Safe!

# Rule 3: Always throttle large async bursts with a Semaphore.
sem = asyncio.Semaphore(100) # Max 100 concurrent requests
async def limited_fetch(url):
    async with sem:
        await fetch(url)
```

*Reference: Fluent Python 2nd ed., Chapter 21 — pages 803–852*
