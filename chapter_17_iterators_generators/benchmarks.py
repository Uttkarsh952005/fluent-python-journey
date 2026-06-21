"""
Chapter 17: Benchmarks — Eager Lists vs Lazy Generators
=======================================================
Comparing the peak memory footprint of building a list in memory (eager)
versus yielding values one-by-one via a generator (lazy).
"""

import sys
import tracemalloc

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Data Sources ─────────────────────────────────────────────────────────────

def eager_builder(n: int) -> list:
    """Builds the entire collection in memory at once."""
    return [x ** 2 for x in range(n)]

def lazy_generator(n: int):
    """Yields one item at a time, keeping nothing in memory."""
    for x in range(n):
        yield x ** 2

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark: Memory Usage (Eager vs Lazy)")
    
    iters = 2_000_000
    print(f"  (Processing {iters:,} integers)\n")
    
    # 1. Eager List Benchmark
    tracemalloc.start()
    data_list = eager_builder(iters)
    # Sum it to ensure it's evaluated
    total_list = sum(data_list) 
    _, peak_eager = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Clear memory
    del data_list 
    
    # 2. Lazy Generator Benchmark
    tracemalloc.start()
    data_gen = lazy_generator(iters)
    total_gen = sum(data_gen)
    _, peak_lazy = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    assert total_list == total_gen, "Calculations drifted!"

    # Format output
    mb_eager = peak_eager / 1024 / 1024
    mb_lazy = peak_lazy / 1024 / 1024

    print(f"  {'Method':<25} {'Peak Memory (MB)':>15}")
    print("  " + "-" * 41)
    print(f"  {'Eager List (in memory)':<25} {mb_eager:>15.2f}")
    print(f"  {'Lazy Generator (yield)':<25} {mb_lazy:>15.5f}")
    
    print(f"\n  Conclusion: The list consumed ~{mb_eager:.1f} MB.")
    print(f"  The generator consumed ~{mb_lazy * 1024:.1f} KB (nearly zero).")
    print("  Generators process data in O(1) memory, allowing you to")
    print("  stream infinitely large files without crashing your server.")

if __name__ == "__main__":
    run_benchmarks()
