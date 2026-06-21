# Chapter 20: Concurrent Executors — Notes

## 1. The Power of `concurrent.futures`
Before Python 3.2, developers had to manually instantiate `threading.Thread` objects, manually call `.start()`, and manually build `queue.Queue` objects to pass data back and forth. 
`concurrent.futures` abstracts all of this away. You simply give the `ThreadPoolExecutor` (or `ProcessPoolExecutor`) a function and some data, and it manages the lifecycle, queuing, and result retrieval for you.

## 2. What is a `Future`?
A `Future` is a core concept in modern concurrency. It is an object that represents the *eventual* result of an asynchronous operation.
*   When you call `executor.submit(func)`, it returns a `Future` instantly.
*   You can check `future.done()` to see if it has finished (returns `True` or `False`).
*   You can call `future.result()`. If the task is finished, it returns the value immediately. If it is still running, `result()` **blocks the main thread** until the worker finishes.

## 3. `executor.map()` vs `executor.submit()`
*   **`map(func, iter)`:** Designed to be a drop-in replacement for Python's built-in `map()`. It is incredibly easy to use. However, it yields results in the **exact same order** as the input iterable. If Task 1 takes 10 seconds, and Task 2 takes 1 second, `map` will block for 10 seconds before yielding Task 1, even though Task 2 is already done.
*   **`submit(func, arg)`:** Designed for granular control. It allows you to submit disparate tasks with different arguments. When combined with `futures.as_completed([futures])`, you can process the results **as they finish**, completely out of order. This is the professional standard for building responsive CLI tools or progress bars.

## 4. The `with` Block Guarantee
You should almost always instantiate an executor inside a `with` block:
```python
with futures.ThreadPoolExecutor() as executor:
    executor.map(...)
```
When the `with` block exits, the context manager's `__exit__` method automatically calls `executor.shutdown(wait=True)`. This guarantees that the main Python script will not exit until all background threads have cleanly finished their work.
