# Chapter 19 — Concurrency Models in Python

> **Theme**: Concurrency is not Parallelism. Python offers three deeply distinct paradigms (Threads, Processes, Asyncio) to solve the exact same problem: waiting for things to finish.

## What You'll Learn

| Paradigm | Concurrency | Parallelism | Best For | Caveat |
|----------|-------------|-------------|----------|--------|
| **Threads** | Preemptive | No (GIL) | Network I/O, File I/O | Race conditions, limited scaling |
| **Processes** | Preemptive | Yes | Heavy Math, CPU load | High memory overhead |
| **Asyncio** | Cooperative | No (GIL) | Heavy Network I/O | Complex syntax, blocking traps |

## Key Files

- [`examples.py`](examples.py) — The exact same console Spinner animation built with `threading`, `multiprocessing`, and `asyncio`.
- [`exercises.py`](exercises.py) — Proving the GIL does not protect you from race conditions, and why `threading.Lock` is mandatory.
- [`mini_project.py`](mini_project.py) — A ThreadPool API scraper proving how to easily parallelize network requests.
- [`benchmarks.py`](benchmarks.py) — Benchmark proving threads speed up `sleep()` by 20x, but speed up `math` by 0x.
- [`notes.md`](notes.md) — The exact mechanics of the Global Interpreter Lock (GIL) and its loopholes.
- [`pitfalls.md`](pitfalls.md) — The trap of using threads for CPU work, and the multiprocessing zombie leak.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — How the CPython OS-level lock actually functions (`sys.setswitchinterval`).

## 30-Second Rules

```python
# Rule 1: Use ThreadPoolExecutor for making HTTP requests or reading disks.
with concurrent.futures.ThreadPoolExecutor() as ex:
    results = ex.map(download_url, urls)

# Rule 2: Use ProcessPoolExecutor for doing heavy math or image processing.
with concurrent.futures.ProcessPoolExecutor() as ex:
    results = ex.map(calculate_primes, numbers)

# Rule 3: Use Asyncio when you need to handle 10,000+ simultaneous network connections.
```

*Reference: Fluent Python 2nd ed., Chapter 19 — pages 723–750*
