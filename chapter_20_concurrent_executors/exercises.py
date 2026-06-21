"""
Chapter 20: Exercises — The Silent Exception Trap
=================================================
Original exercises demonstrating why ThreadPoolExecutors can be
dangerous: they silently swallow exceptions inside worker threads
unless you explicitly retrieve the result.
"""

import sys
import time
from concurrent import futures

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Silent Failure
# ─────────────────────────────────────────────────────────────────────────────

def fragile_worker(task_id: int) -> str:
    print(f"  [Worker {task_id}] Started...")
    time.sleep(0.1)
    if task_id == 2:
        # FATAL ERROR!
        raise RuntimeError(f"Task {task_id} crashed spectacularly!")
    return f"Success {task_id}"

def test_ex1_silent_exception() -> None:
    section("Exercise 1: The Silent Exception")
    
    print("  Submitting 3 tasks (Task 2 is rigged to crash)...")
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future1 = executor.submit(fragile_worker, 1)
        future2 = executor.submit(fragile_worker, 2)
        future3 = executor.submit(fragile_worker, 3)
        
    # Notice we exit the `with` block here. The executor shutdown() guarantees 
    # all threads have finished. But the program DID NOT CRASH!
    print("\n  [Main] Executor finished. Did the program crash? NO!")
    print("  The exception was caught and stuffed inside future2.")
    
    # We must explicitly check the exception, or call .result() to raise it.
    exc = future2.exception()
    print(f"  future2.exception() -> {exc}")
    
    print("\n✓ Exercise 1 passed: Proved that Executors swallow exceptions into Futures.")
    print("  ALWAYS call .result() or .exception() on your futures to prevent silent bugs!")


if __name__ == "__main__":
    test_ex1_silent_exception()
