# Chapter 20 — Architecture Notes: `concurrent.futures` Internals

---

## 1. The Work Queue Architecture

Under the hood, a `ThreadPoolExecutor` is powered by the `queue.Queue` class (which is a thread-safe FIFO queue native to Python).
When you call `executor.submit(func, *args)`, the Executor does not immediately spawn a thread. Instead:
1. It wraps your function in a `_WorkItem` object.
2. It pushes that `_WorkItem` into its internal `work_queue`.
3. It creates an empty `Future` object, links it to the `_WorkItem`, and returns the `Future` to you.

The worker threads run an infinite loop (`_worker()`). They constantly call `work_queue.get(block=True)`. When a `_WorkItem` arrives, a worker pulls it, executes the function, takes the return value (or exception), and manually inserts it into the `Future` object using `future.set_result(val)` or `future.set_exception(exc)`.

---

## 2. The Mechanics of `as_completed`

How does `futures.as_completed()` quickly know when *any* future is done, without constantly polling all of them?

When you pass a list of futures to `as_completed()`, it leverages the `.add_done_callback()` method that exists on all `Future` objects.
It attaches an internal callback to every single future. When a worker thread finishes a task and calls `future.set_result()`, that action immediately triggers the callback. The callback pushes that completed `Future` object onto a centralized `yield_queue`.
The main thread simply blocks on `yield_queue.get()`, ensuring it gets the completed futures exactly in the order they finish.

---

## 3. The Waiter Thread in `ProcessPoolExecutor`

`ProcessPoolExecutor` is significantly more complex than `ThreadPoolExecutor` because you cannot share memory (like Future objects) across OS processes.
It uses a completely separate background thread called the `QueueManagerThread`. 
When you submit a task to `ProcessPoolExecutor`, it is serialized using `pickle`, passed through an OS Pipe to the child process, executed, serialized again, and passed back through the pipe. The `QueueManagerThread` sits in the background, constantly pulling the pickled results out of the pipe and injecting them into the memory-local `Future` objects in the parent process.
