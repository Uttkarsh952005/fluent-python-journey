# Chapter 19: Concurrency Models — Notes

## 1. Concurrency vs. Parallelism
*   **Concurrency:** Handling multiple tasks at the same time. (e.g., A chef chopping vegetables, stopping to check the oven, then returning to chopping). Achieved via Threads or Asyncio.
*   **Parallelism:** Executing multiple tasks at the exact same physical time. (e.g., Two chefs in the kitchen, one chopping, one baking). Achieved in Python *only* via `multiprocessing`.

## 2. The Global Interpreter Lock (GIL)
CPython's memory management is not thread-safe. To prevent two threads from simultaneously altering an object's reference count (which could crash the interpreter), CPython uses the GIL.
*   The GIL allows only **one native OS thread** to execute Python bytecodes at any given moment.
*   **The Crucial Loophole:** Whenever a thread performs an I/O operation (reading a file, sending a network request, or `time.sleep()`), it **releases the GIL**. This allows another thread to execute Python code while the first thread waits for the hardware.
*   This is why Threads are useless for CPU-bound tasks in Python (math), but spectacular for I/O-bound tasks (web scraping).

## 3. The Three Paradigms
1.  **`threading`:** Preemptive. The OS forcibly pauses threads and switches contexts. Threads share the same memory space, making data sharing easy but requiring `Lock` objects to prevent race conditions.
2.  **`multiprocessing`:** Preemptive. Launches completely separate CPython processes. Bypasses the GIL. Perfect for heavy CPU-bound tasks. Massive memory and startup overhead.
3.  **`asyncio`:** Cooperative. Runs on a single thread with a single event loop. Tasks voluntarily yield control using the `await` keyword. Because there is only one thread, race conditions are largely eliminated, and the memory overhead per task is microscopic compared to threads.
