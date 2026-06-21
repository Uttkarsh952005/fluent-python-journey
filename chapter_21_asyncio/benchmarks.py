"""
Chapter 21: Benchmarks — asyncio.to_thread
==========================================
How do you run a blocking synchronous function (like reading a huge file
or using requests.get) inside an async application without freezing it?

This benchmark proves the necessity and power of `asyncio.to_thread`.
"""

import sys
import time
import asyncio

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Tasks ────────────────────────────────────────────────────────────────────

def blocking_legacy_function():
    """A legacy synchronous function that we cannot rewrite."""
    time.sleep(0.5)
    return "Legacy Data"

async def background_pulse():
    """A lightweight task that should pulse every 0.1s continuously."""
    pulses = 0
    while True:
        await asyncio.sleep(0.1)
        pulses += 1
        print(f"  [Pulse] Heartbeat {pulses}")

# ── Runners ──────────────────────────────────────────────────────────────────

async def run_bad_scenario():
    """Demonstrates freezing the event loop."""
    print("  Starting legacy blocking function directly...")
    # This completely halts the main thread. The background pulse dies.
    blocking_legacy_function()
    print("  Legacy function finished.\n")

async def run_good_scenario():
    """Demonstrates safe offloading."""
    print("  Starting legacy blocking function via to_thread()...")
    # This safely offloads the blocking call to a background thread pool.
    # The main thread remains totally free to run the heartbeat pulse!
    await asyncio.to_thread(blocking_legacy_function)
    print("  Legacy function finished.\n")

# ── Benchmarks ───────────────────────────────────────────────────────────────

async def main():
    section("Scenario 1: The Blocking Freeze")
    # Start the heartbeat in the background
    pulse_task = asyncio.create_task(background_pulse())
    
    # Run the bad code
    await run_bad_scenario()
    
    pulse_task.cancel() # Stop the heartbeat
    
    
    section("Scenario 2: Safe Offloading via to_thread")
    pulse_task = asyncio.create_task(background_pulse())
    
    # Run the good code
    await run_good_scenario()
    
    pulse_task.cancel()
    
    print("Conclusion:")
    print("In Scenario 1, the event loop was frozen, so 0 heartbeats occurred.")
    print("In Scenario 2, to_thread kept the loop alive, allowing ~5 heartbeats.")

if __name__ == "__main__":
    asyncio.run(main())
