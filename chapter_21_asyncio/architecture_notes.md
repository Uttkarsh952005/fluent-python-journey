# Chapter 21 — Architecture Notes: The Event Loop and Selectors

---

## 1. Cooperative Yielding via `await`

In a multithreaded architecture (Chapter 19), the OS interrupts your thread via preemptive scheduling.
In `asyncio`, the event loop is entirely written in Python. It relies on generators.

When you call `await asyncio.sleep(1)`, you are essentially calling `yield` deep down in the CPython async infrastructure.
This `yield` suspends the coroutine's internal `PyFrameObject` (the same frame object we discussed in Chapter 17) and returns control to the `asyncio` event loop. The event loop then looks at its internal queue of ready tasks and invokes `.send()` on the next one.

---

## 2. The `selectors` Module

How does the event loop know *when* a network request is finished without constantly checking (polling) it and burning CPU?

Python's `asyncio` loop is built on top of the OS-level `select` or `epoll` APIs (via the standard library `selectors` module).
When a coroutine makes an HTTP request, it creates a non-blocking TCP socket. It registers that socket's file descriptor with the OS kernel, saying: *"Wake me up when this socket has data to read."*

The coroutine then yields control.
The event loop executes other tasks until all tasks are waiting on sockets.
At that exact moment, the event loop makes a single blocking call to the OS kernel (`epoll_wait` on Linux, or `kqueue` on Mac). The OS kernel physically halts the Python thread with 0% CPU usage.
When a packet arrives over the network, the OS kernel wakes up the Python thread, hands it a list of sockets that are ready, and the event loop resumes the specific coroutines waiting on those sockets.

---

## 3. High Performance with `uvloop`

The default Python event loop is fast, but it is written in pure Python.
Because `asyncio` provides a strict, pluggable API for event loops, you can replace the default loop with `uvloop`.
`uvloop` is an event loop written in Cython built on top of `libuv` (the exact same C library that powers Node.js). Switching to `uvloop` can significantly increase the throughput of an `asyncio` application by drastically reducing the overhead of context switching and socket management.
