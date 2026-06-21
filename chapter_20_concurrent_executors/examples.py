"""
Chapter 20: Concurrent Executors
================================
Original implementations exploring the concurrent.futures module,
including map(), submit(), Futures, and as_completed().

Key concepts covered:
- executor.map() for ordered processing
- executor.submit() for manual Future management
- as_completed() for responsive out-of-order processing
"""

import sys
import time
import random
from concurrent import futures

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. executor.map() (Ordered Results)
# ─────────────────────────────────────────────────────────────────────────────

def worker_map(task_id: int) -> str:
    """A worker that sleeps randomly, simulating network jitter."""
    sleep_time = random.uniform(0.1, 0.5)
    time.sleep(sleep_time)
    return f"Task {task_id} done (slept {sleep_time:.2f}s)"

def demo_executor_map() -> None:
    section("Part 1: executor.map()")
    
    # map() guarantees that the results are returned in the exact same
    # order as the input iterable, even if Task 3 finishes before Task 1!
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(worker_map, range(3))
        
        for res in results:
            # This loop will block if the next result in sequence isn't ready
            print(f"  Result: {res}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. executor.submit() and Futures
# ─────────────────────────────────────────────────────────────────────────────

def worker_submit(name: str) -> str:
    time.sleep(0.2)
    return f"Hello, {name}!"

def demo_executor_submit() -> None:
    section("Part 2: submit() and Futures")
    
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        # submit() does not block! It instantly returns a Future object.
        future = executor.submit(worker_submit, "Alice")
        
        print(f"  Future created. Is it done? {future.done()}")
        
        # Calling .result() explicitly blocks the main thread until the Future completes.
        result = future.result()
        print(f"  Future completed. Result: '{result}'")


# ─────────────────────────────────────────────────────────────────────────────
# 3. as_completed() (Out-of-Order Processing)
# ─────────────────────────────────────────────────────────────────────────────

def worker_unpredictable(task_id: int) -> int:
    """Sleeps randomly."""
    time.sleep(random.uniform(0.1, 0.8))
    return task_id

def demo_as_completed() -> None:
    section("Part 3: as_completed() for Responsive UI")
    
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        # 1. Submit all tasks and gather the Future objects
        pending_futures = []
        for i in range(5):
            pending_futures.append(executor.submit(worker_unpredictable, i))
            
        # 2. Process them EXACTLY as they finish, regardless of starting order.
        # This is strictly superior for progress bars and UI responsiveness.
        for future in futures.as_completed(pending_futures):
            res = future.result()
            print(f"  Task {res} finished!")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_executor_map()
    demo_executor_submit()
    demo_as_completed()
