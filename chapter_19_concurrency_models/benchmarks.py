"""
Chapter 19: Benchmarks — CPU Bound vs I/O Bound
===============================================
This benchmark proves the fundamental law of Python Concurrency:
- Threads speed up I/O bound tasks (because they release the GIL).
- Threads DO NOT speed up CPU bound tasks (because the GIL blocks them).
"""

import sys
import time
from concurrent import futures

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Tasks ────────────────────────────────────────────────────────────────────

def cpu_heavy_task(n: int) -> int:
    """Math operations: Binds the CPU, holds the GIL tightly."""
    count = 0
    for i in range(10_000_000):
        count += i
    return count

def io_heavy_task(n: int) -> int:
    """Network/Disk operations: Idles the CPU, releases the GIL."""
    time.sleep(0.1)
    return n

# ── Runners ──────────────────────────────────────────────────────────────────

def run_sequential(task_func, count):
    for i in range(count):
        task_func(i)

def run_threaded(task_func, count):
    with futures.ThreadPoolExecutor(max_workers=count) as executor:
        list(executor.map(task_func, range(count)))

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark 1: I/O-Bound Task (sleep)")
    count_io = 20 # 20 tasks, 0.1s each
    
    t0 = time.perf_counter()
    run_sequential(io_heavy_task, count_io)
    seq_io_time = time.perf_counter() - t0
    
    t0 = time.perf_counter()
    run_threaded(io_heavy_task, count_io)
    thr_io_time = time.perf_counter() - t0
    
    print(f"  Sequential: {seq_io_time:.2f}s")
    print(f"  Threaded:   {thr_io_time:.2f}s  <-- SIGNIFICANT SPEEDUP")
    
    
    section("Benchmark 2: CPU-Bound Task (math)")
    count_cpu = 4
    
    t0 = time.perf_counter()
    run_sequential(cpu_heavy_task, count_cpu)
    seq_cpu_time = time.perf_counter() - t0
    
    t0 = time.perf_counter()
    run_threaded(cpu_heavy_task, count_cpu)
    thr_cpu_time = time.perf_counter() - t0
    
    print(f"  Sequential: {seq_cpu_time:.2f}s")
    print(f"  Threaded:   {thr_cpu_time:.2f}s  <-- ZERO SPEEDUP (Often slower!)")
    
    print("\nConclusion:")
    print("The GIL prevents threads from executing math simultaneously.")
    print("If you need to parallelize math, you must use ProcessPoolExecutor.")

if __name__ == "__main__":
    run_benchmarks()
