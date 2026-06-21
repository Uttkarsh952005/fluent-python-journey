"""
Chapter 19: Concurrency Models in Python
========================================
Original implementations exploring the three major concurrency
paradigms in Python: threading, multiprocessing, and asyncio.

Key concepts covered:
- Preemptive multitasking (Threads & Processes)
- Cooperative multitasking (Asyncio)
- Memory separation (Processes) vs Shared memory (Threads)
"""

import sys
import time
import itertools
import threading
import multiprocessing
import asyncio

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Threading Spinner (Preemptive, Shared Memory, GIL Restricted)
# ─────────────────────────────────────────────────────────────────────────────

def spin_thread(msg: str, done: threading.Event) -> None:
    """A background thread function."""
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)
        if done.wait(0.1): # Wait blocks for 0.1s, returning True if flag is set
            break
    print('\r' + ' ' * len(status) + '\r', end='')

def demo_threading() -> None:
    section("Part 1: Threading (Preemptive)")
    done = threading.Event()
    # Threads share the exact same memory space and are managed by the OS.
    spinner = threading.Thread(target=spin_thread, args=('Thinking (Thread)...', done))
    
    spinner.start()
    time.sleep(2) # Simulating I/O bound work on main thread. GIL is released here!
    done.set()    # Set flag to stop the thread
    spinner.join()
    print("Done threading!")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Multiprocessing Spinner (Preemptive, Isolated Memory, GIL Bypassed)
# ─────────────────────────────────────────────────────────────────────────────

def spin_process(msg: str, done: multiprocessing.Event) -> None:
    """A background process function."""
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)
        if done.wait(0.1): 
            break
    print('\r' + ' ' * len(status) + '\r', end='')

def demo_multiprocessing() -> None:
    section("Part 2: Multiprocessing (Parallelism)")
    # Must use multiprocessing.Event, not threading.Event!
    done = multiprocessing.Event()
    # Processes launch an entirely new Python interpreter. Heavy overhead!
    spinner = multiprocessing.Process(target=spin_process, args=('Thinking (Process)...', done))
    
    spinner.start()
    time.sleep(2) # Simulating CPU/IO bound work
    done.set()
    spinner.join()
    print("Done multiprocessing!")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Asyncio Spinner (Cooperative, Single Thread, Event Loop)
# ─────────────────────────────────────────────────────────────────────────────

async def spin_async(msg: str) -> None:
    """A coroutine managed by the event loop."""
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)
        try:
            # Yield control back to the event loop cooperatively
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            break
    print('\r' + ' ' * len(status) + '\r', end='')

async def run_async_demo() -> None:
    # Schedule the coroutine to run on the event loop
    spinner = asyncio.create_task(spin_async('Thinking (Asyncio)...'))
    
    # Simulate work. `await` yields control back to the loop, letting the spinner run.
    await asyncio.sleep(2) 
    
    # Cancel the task explicitly
    spinner.cancel()
    print("Done asyncio!")

def demo_asyncio() -> None:
    section("Part 3: Asyncio (Cooperative)")
    asyncio.run(run_async_demo())


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # In Windows, multiprocessing MUST be protected by the __main__ block
    demo_threading()
    demo_multiprocessing()
    demo_asyncio()
