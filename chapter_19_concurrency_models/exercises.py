"""
Chapter 19: Exercises — The GIL and the Need for Locks
======================================================
Original exercises demonstrating why the Global Interpreter Lock (GIL)
does NOT protect you from race conditions in multithreaded code.
"""

import sys
import threading

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Race Condition
# ─────────────────────────────────────────────────────────────────────────────
# The GIL ensures that only one thread executes Python bytecodes at a time.
# However, the operation `counter += 1` translates to THREE bytecodes:
# 1. LOAD_GLOBAL (get current value)
# 2. LOAD_CONST (get 1)
# 3. INPLACE_ADD (add them)
# 4. STORE_GLOBAL (save it back)
# The OS can interrupt a thread exactly between step 1 and step 4!

counter = 0

def bad_worker():
    global counter
    for _ in range(100_000):
        # NOT thread-safe!
        counter += 1

def test_ex1_race_condition() -> None:
    section("Exercise 1: Threading Race Condition")
    global counter
    counter = 0
    
    threads = [threading.Thread(target=bad_worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    print(f"Expected: 1,000,000")
    print(f"Actual:   {counter:,}")
    
    if counter != 1_000_000:
        print("✓ Exercise 1 passed: Proved that the GIL does NOT prevent logical race conditions.")
    else:
        print("? Passed by sheer luck. Try running again to see the race condition.")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: The Explicit Lock
# ─────────────────────────────────────────────────────────────────────────────
# To fix the race condition, we must use a threading.Lock to explicitly block
# other threads from executing the critical section.

safe_counter = 0
lock = threading.Lock()

def good_worker():
    global safe_counter
    for _ in range(100_000):
        # A context manager acquires and releases the lock automatically
        with lock:
            safe_counter += 1

def test_ex2_safe_locking() -> None:
    section("Exercise 2: Explicit Locking")
    global safe_counter
    safe_counter = 0
    
    threads = [threading.Thread(target=good_worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    print(f"Expected: 1,000,000")
    print(f"Actual:   {safe_counter:,}")
    assert safe_counter == 1_000_000
    print("✓ Exercise 2 passed: Proved that explicit Locks guarantee thread safety.")


if __name__ == "__main__":
    test_ex1_race_condition()
    test_ex2_safe_locking()
