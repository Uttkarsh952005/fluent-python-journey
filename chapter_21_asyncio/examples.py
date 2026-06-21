"""
Chapter 21: Asynchronous Programming
====================================
Original implementations exploring native async/await syntax,
the asyncio event loop, and concurrent task coordination.

Key concepts covered:
- Coroutines (async def / await)
- asyncio.gather() for ordered concurrent execution
- asyncio.as_completed() for out-of-order responsiveness
"""

import sys
import asyncio
import random
import time

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Native Coroutines
# ─────────────────────────────────────────────────────────────────────────────

async def fetch_data(id: int) -> str:
    """A native coroutine. Must be called with `await`."""
    print(f"  [Task {id}] Starting fetch...")
    # await yields control back to the event loop, allowing other tasks to run
    await asyncio.sleep(0.5) 
    print(f"  [Task {id}] Finished!")
    return f"Data_{id}"

async def run_part_1() -> None:
    section("Part 1: Basic await")
    # Sequential awaiting (Slow! Takes 1.0s total)
    res1 = await fetch_data(1)
    res2 = await fetch_data(2)
    print(f"  Results: {res1}, {res2}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. asyncio.gather() (Concurrent & Ordered)
# ─────────────────────────────────────────────────────────────────────────────

async def run_part_2() -> None:
    section("Part 2: asyncio.gather()")
    # gather() schedules all coroutines to run CONCURRENTLY.
    # It waits for all of them to finish, and returns the results
    # in the exact same order they were passed in.
    
    start_t = time.perf_counter()
    # Runs in 0.5s total!
    results = await asyncio.gather(
        fetch_data(10),
        fetch_data(11),
        fetch_data(12)
    )
    elapsed = time.perf_counter() - start_t
    
    print(f"  Results: {results} (Took {elapsed:.2f}s)")


# ─────────────────────────────────────────────────────────────────────────────
# 3. asyncio.as_completed() (Out-of-Order UI)
# ─────────────────────────────────────────────────────────────────────────────

async def variable_fetch(id: int) -> str:
    await asyncio.sleep(random.uniform(0.1, 0.9))
    return f"Data_{id}"

async def run_part_3() -> None:
    section("Part 3: asyncio.as_completed()")
    
    # Create the coroutine objects (they don't start running yet!)
    coros = [variable_fetch(i) for i in range(5)]
    
    # as_completed yields futures exactly as they finish
    for coro in asyncio.as_completed(coros):
        # We must await the yielded future to get the actual result
        result = await coro
        print(f"  Received: {result}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EVENT LOOP
# ─────────────────────────────────────────────────────────────────────────────

async def main() -> None:
    await run_part_1()
    await run_part_2()
    await run_part_3()

if __name__ == "__main__":
    # asyncio.run() bootstraps the event loop, runs the main coroutine,
    # and safely tears down the loop when finished.
    asyncio.run(main())
