# Chapter 20 — Pitfalls: Concurrent Executors

---

## Pitfall 1: The Silent Memory Explosion

When you use `executor.map()` or `executor.submit()`, you are pushing tasks into the executor's internal queue. If your producer (the `for` loop) generates tasks faster than the workers can complete them, your RAM usage will skyrocket.

```python
from concurrent.futures import ThreadPoolExecutor

def fetch_db_record(user_id):
    pass # Slow operation

def massive_migration():
    # BUG: If you have 50 million users, this will instantly submit 
    # 50 million Future objects into memory, crashing your server!
    user_ids = range(50_000_000) 
    with ThreadPoolExecutor(max_workers=20) as ex:
        results = ex.map(fetch_db_record, user_ids)
```

**Why it fails:** `ThreadPoolExecutor` does not natively have backpressure. It accepts infinite tasks into its queue.
**Fix:** You must chunk your iterator. Feed the executor 1,000 tasks, wait for them to finish, then feed the next 1,000. Use `itertools.islice`.

---

## Pitfall 2: The Silent Exception

We covered this heavily in `exercises.py`. If a worker thread throws an exception, the thread dies, but the executor catches the exception and stores it inside the `Future` object.

```python
with ThreadPoolExecutor() as ex:
    # This throws a ValueError internally
    ex.submit(int, "NOT_A_NUMBER")

print("Finished successfully!") # The developer thinks it worked!
```

**Fix:** If you are using `.submit()`, you must explicitly collect the futures and call `.result()` on them, or the errors will be buried forever.

---

## Pitfall 3: `ProcessPoolExecutor` without `__main__`

If you change `ThreadPoolExecutor` to `ProcessPoolExecutor` to speed up CPU-bound tasks, you might inadvertently create a fork-bomb on Windows.

**Fix:** Just like raw `multiprocessing`, any script utilizing `ProcessPoolExecutor` on Windows must have its execution protected by `if __name__ == "__main__":`.
