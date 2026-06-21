# Chapter 21 — Interview Questions: Asynchronous Programming

---

## 🟢 L3

### Q1: Can `asyncio` utilize multiple CPU cores?
No. An `asyncio` event loop runs entirely on a single thread. It achieves massive concurrency through cooperative multitasking (rapidly switching between tasks while waiting for I/O), not through parallelism. If you need multi-core parallelism, you must use `multiprocessing`.

---

## 🟡 L4

### Q2: What happens if you run `time.sleep(5)` inside an `async def` function?
You will completely freeze the event loop for 5 seconds. Because `asyncio` is single-threaded, `time.sleep` blocks the entire thread. No other coroutines, network requests, or background tasks will be able to execute during that time. You must use `await asyncio.sleep(5)` instead, which yields control back to the loop.

---

## 🔴 L5

### Q3: How do you prevent `asyncio.gather` from crashing your server with "Too Many Open Files" when requesting 100,000 URLs?
`asyncio` does not have a built-in max-concurrency cap like `ThreadPoolExecutor` does. It will instantly attempt to open all 100,000 sockets simultaneously. To prevent this, you must instantiate an `asyncio.Semaphore(limit)` and wrap your network request code in an `async with semaphore:` block to throttle the execution rate.

---

## 🟣 L6

### Q4: How does `asyncio.to_thread()` work under the hood?
When you pass a legacy blocking function to `asyncio.to_thread()`, it does not run it on the event loop. Instead, `to_thread` gets the current event loop and calls `loop.run_in_executor()`. This passes the blocking function to a hidden, default `ThreadPoolExecutor` managed by `asyncio`. The function executes in a background thread, while the main thread (and the event loop) remains completely free to continue processing other coroutines.
