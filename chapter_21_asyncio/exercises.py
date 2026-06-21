"""
Chapter 21: Exercises — The Blocking Trap
=========================================
Original exercises demonstrating the #1 most common architectural 
mistake in async Python: using a blocking synchronous function 
inside an asynchronous event loop.
"""

import sys
import time
import asyncio

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Blocking Trap
# ─────────────────────────────────────────────────────────────────────────────
# The event loop runs entirely on ONE thread.
# If a single coroutine calls a blocking function (like time.sleep or 
# requests.get), the ENTIRE loop is frozen. No other coroutines can run!

async def good_async_task(id: int):
    print(f"  [Task {id}] (Async) Started.")
    # Yields control back to the loop. Other tasks can run!
    await asyncio.sleep(0.5) 
    print(f"  [Task {id}] (Async) Finished.")

async def bad_blocking_task(id: int):
    print(f"  [Task {id}] (BLOCKING) Started... freezing the entire app!")
    # FATAL MISTAKE: time.sleep() does not yield control. 
    # It halts the actual OS thread. The event loop is completely dead for 1s.
    time.sleep(1.0) 
    print(f"  [Task {id}] (BLOCKING) Finished.")

async def test_ex1_blocking_trap() -> None:
    section("Exercise 1: The Blocking Trap")
    
    print("  Scenario: Scheduling 2 good tasks and 1 bad task concurrently.")
    start_t = time.perf_counter()
    
    await asyncio.gather(
        good_async_task(1),
        bad_blocking_task(99),  # This will hijack the whole system
        good_async_task(2)
    )
    
    elapsed = time.perf_counter() - start_t
    print(f"\n  Total time: {elapsed:.2f}s")
    print("✓ Exercise 1 passed: Notice how the async tasks were completely")
    print("  paralyzed until the bad task finished its time.sleep()!")


if __name__ == "__main__":
    asyncio.run(test_ex1_blocking_trap())
