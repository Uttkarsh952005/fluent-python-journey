# Chapter 21: Asynchronous Programming — Notes

## 1. The Event Loop Architecture
`asyncio` does **not** use multiple threads to achieve concurrency. It uses exactly **one thread** and an **Event Loop**.
The event loop acts like a highly efficient traffic cop. It tracks multiple tasks. When Task A needs to wait for a network request, it explicitly yields control back to the event loop using the `await` keyword. The event loop instantly switches execution to Task B.

## 2. Terminology
*   **Coroutine Function:** A function defined with `async def`. When called, it does *not* execute. Instead, it returns a Coroutine Object.
*   **Coroutine Object:** The object returned by an `async def` function. It must be driven by the event loop, usually via `await`.
*   **Awaitable:** Any object that can be used with the `await` keyword. This includes Coroutines, Tasks, and Futures.

## 3. The `asyncio` Core APIs
*   **`asyncio.run(coro)`:** The entry point. It creates a brand new event loop, runs the main coroutine until it finishes, and cleanly shuts the loop down.
*   **`await`:** Pauses the current coroutine, allowing the event loop to switch to other pending tasks until the awaited operation finishes.
*   **`asyncio.gather(*awaitables)`:** Schedules multiple tasks to run concurrently. It pauses the current coroutine until *all* of them are finished, then returns their results as a list in the exact order they were passed in.
*   **`asyncio.create_task(coro)`:** Schedules a coroutine to run on the event loop immediately "in the background", returning a Task object. You don't have to `await` it immediately.

## 4. The Golden Rule of Async
**Never block the event loop.**
Because there is only one thread, if you execute a blocking synchronous function (like `requests.get()`, `time.sleep()`, or massive mathematical loops) inside a coroutine, the thread halts. The event loop freezes. **Zero other tasks can run.** Every single connected client to your server will hang. If you must use blocking code, you must offload it using `asyncio.to_thread()`.
