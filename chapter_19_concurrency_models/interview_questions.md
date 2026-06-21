# Chapter 19 — Interview Questions: Concurrency

---

## 🟢 L3

### Q1: Can a multithreaded Python program utilize multiple CPU cores?
No (not for executing Python code). The Global Interpreter Lock (GIL) ensures that only one native thread executes Python bytecodes at any given time, regardless of how many CPU cores the machine has. If you need to utilize multiple cores for math processing, you must use `multiprocessing`.

---

## 🟡 L4

### Q2: If the GIL prevents multiple threads from running simultaneously, why do we use `threading` at all?
Because the GIL is released during I/O operations. When a thread requests data from the network (`requests.get()`) or reads from disk, it drops the GIL and goes to sleep while waiting for the OS hardware. This allows the Python interpreter to immediately schedule another thread. For heavily I/O-bound tasks, threading provides massive speedups because you can wait on 100 network requests simultaneously.

---

## 🔴 L5

### Q3: What is the primary architectural difference between `threading` and `multiprocessing` regarding memory?
Threads share the exact same memory space (the same Python interpreter process). This makes it very easy to share data (like global variables), but requires you to carefully manage Race Conditions using `Lock` objects.
Processes (`multiprocessing`) spawn entirely new OS processes, each containing its own isolated Python interpreter and memory space. They cannot accidentally overwrite each other's variables, but sharing data between them requires expensive inter-process communication (IPC) serialization via Queues or Pipes.

---

## 🟣 L6

### Q4: Explain the difference between "Preemptive" and "Cooperative" multitasking in Python.
**Preemptive** multitasking is used by `threading` and `multiprocessing`. The operating system (OS) is in complete control. It decides when to pause a thread/process and switch to another one. Your code has no say in when it gets interrupted.
**Cooperative** multitasking is used by `asyncio`. It runs entirely on a single thread. The event loop cannot forcibly interrupt a running coroutine. Instead, the coroutine must voluntarily pause and hand control back to the event loop using the `await` keyword. Because the code dictates exactly when context switches occur, race conditions are practically eliminated.
