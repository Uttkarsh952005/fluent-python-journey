# Chapter 19 — Pitfalls: Concurrency

---

## Pitfall 1: Using Threads for CPU-Bound Work

Because threads represent true OS-level parallel execution in languages like C++ and Java, developers instinctively reach for `threading` when they have a heavy math or data processing job.

```python
import threading

def crunch_numbers():
    return sum(x*x for x in range(10_000_000))

# BUG: Developer assumes these two threads will run on two CPU cores
# and finish in half the time.
t1 = threading.Thread(target=crunch_numbers)
t2 = threading.Thread(target=crunch_numbers)
t1.start(); t2.start()
t1.join(); t2.join()
```

**Why it fails:** The Global Interpreter Lock (GIL) strictly prevents two native threads from executing Python bytecodes at the same time. The OS will rapidly switch between `t1` and `t2`, forcing them to share a single CPU core. In fact, due to the overhead of context switching, this threaded code will often execute **slower** than just running it sequentially.
**Fix:** Use `multiprocessing.Process` or `concurrent.futures.ProcessPoolExecutor` to spawn completely separate CPython instances.

---

## Pitfall 2: Forgetting to protect shared state

A massive misconception is that because the GIL only allows one thread to run at a time, Python is natively thread-safe.

```python
users_active = 0

def login_user():
    global users_active
    # BUG: This is 4 separate bytecodes. The OS can pause the thread 
    # right after reading the value, before saving the new one!
    users_active += 1 
```

**Fix:** The GIL protects CPython's internal memory (like object reference counts). It does **not** protect your application logic. Always use `threading.Lock()` around any shared mutable state.

---

## Pitfall 3: The `multiprocessing` Windows Trap

On Linux, `multiprocessing` uses `fork()`, which safely clones the parent process state. On Windows, `fork()` doesn't exist. Windows must use `spawn()`, which imports and executes the entire script from the top in the new process.

```python
import multiprocessing

def worker():
    print("Working")

# BUG ON WINDOWS: This will recursively spawn infinite processes until the OS crashes!
p = multiprocessing.Process(target=worker)
p.start()
```

**Why it fails:** When Windows spawns the child process, it imports the script. During the import, it hits `p.start()` again, spawning a grandchild process, which hits `p.start()`, ad infinitum.
**Fix:** On Windows, all multiprocessing code **must** be protected behind the `if __name__ == '__main__':` guard.
