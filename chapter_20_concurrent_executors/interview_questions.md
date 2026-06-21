# Chapter 20 — Interview Questions: Concurrent Executors

---

## 🟢 L3

### Q1: What is the main advantage of using `concurrent.futures` over `threading.Thread`?
It provides a much higher-level abstraction. You don't have to manually instantiate threads, call `.start()`, or manually set up thread-safe `Queue` objects to retrieve return values or exceptions. You just instantiate an Executor, pass it a function, and it handles the entire lifecycle for you.

---

## 🟡 L4

### Q2: What is the exact difference between `executor.map()` and `futures.as_completed()`?
*   `executor.map()` blocks the iterator until the *next* result in the original sequence is ready. It strictly preserves the order of the input list.
*   `futures.as_completed()` yields results the exact millisecond they finish, completely out of order. This is highly preferred for building responsive UI applications because you don't have to wait for the slowest task to finish just to see the fastest task's result.

---

## 🔴 L5

### Q3: How do Executors handle exceptions raised in worker threads?
If a worker thread raises an exception, the thread will terminate, but the main Python process will *not* crash. Instead, the Executor catches the exception and stores it inside the `Future` object corresponding to that task. The exception is only re-raised in the main thread if you explicitly call `future.result()`. If you never call `.result()`, the exception is silently swallowed.

---

## 🟣 L6

### Q4: Why is it critical to instantiate an Executor inside a `with` block?
The context manager protocol (`__enter__` and `__exit__`) in Executors is designed as a safety net. The `__exit__` method automatically calls `executor.shutdown(wait=True)`. This completely blocks the main thread from exiting until all running worker threads have successfully finished their tasks. Without this `with` block, your main script could finish and exit while background threads are still writing to a database, resulting in data corruption.
