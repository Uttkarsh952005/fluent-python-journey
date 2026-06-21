"""
Chapter 20: Benchmarks — map() vs as_completed()
================================================
Comparing the Time-To-First-Result (TTFR) of map() vs as_completed().
When building responsive applications, you want to yield data to the
user immediately, rather than blocking on the slowest task.
"""

import sys
import time
from concurrent import futures

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Tasks ────────────────────────────────────────────────────────────────────

def slow_then_fast(task_id: int) -> int:
    """
    Task 0 takes 2.0 seconds.
    Tasks 1-4 take 0.1 seconds.
    """
    if task_id == 0:
        time.sleep(2.0)
    else:
        time.sleep(0.1)
    return task_id

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark: executor.map() (Ordered)")
    print("  Notice how the program completely stalls for 2 seconds")
    print("  because it refuses to yield Task 1 until Task 0 is done!\n")
    
    t0 = time.perf_counter()
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        for result in executor.map(slow_then_fast, range(5)):
            elapsed = time.perf_counter() - t0
            print(f"  [{elapsed:0.2f}s] Received Task {result}")
            

    section("Benchmark: as_completed() (Out of Order)")
    print("  Notice how Tasks 1-4 are yielded quickly to the user,")
    print("  and Task 0 is yielded last.\n")
    
    t0 = time.perf_counter()
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        pending = [executor.submit(slow_then_fast, i) for i in range(5)]
        
        for future in futures.as_completed(pending):
            result = future.result()
            elapsed = time.perf_counter() - t0
            print(f"  [{elapsed:0.2f}s] Received Task {result}")
            
    print("\nConclusion:")
    print("If your goal is a responsive UI or live progress bar,")
    print("as_completed() is strictly superior to map().")

if __name__ == "__main__":
    run_benchmarks()
