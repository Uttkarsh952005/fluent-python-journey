"""
Chapter 12: Benchmarks — Short-Circuit Equality vs Tuple Conversion
===================================================================
Compares the performance of evaluating __eq__ using short-circuiting
(zip + all) versus converting sequences to large tuples.
"""

import sys
import timeit

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Setup ────────────────────────────────────────────────────────────────────

SETUP_CODE = """
from array import array

# Two huge vectors of 1,000,000 floats
v1 = array('d', [1.0] * 1_000_000)
v2 = array('d', [1.0] * 1_000_000)

# Make them differ at index 5 to test short-circuiting
v2[5] = 9.9
"""

TEST_TUPLE = """
# Inefficient: converts entire 1M-element array to a tuple before comparing
res = tuple(v1) == tuple(v2)
"""

TEST_ZIP = """
# Efficient: zips iteratively, all() short-circuits at index 5
res = len(v1) == len(v2) and all(a == b for a, b in zip(v1, v2))
"""

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark: Fast Equality vs Tuple Conversion")
    print("  Comparing two 1,000,000 element vectors.")
    print("  They differ at index 5.\n")
    
    # Run tests
    iters = 100
    time_tuple = timeit.timeit(TEST_TUPLE, setup=SETUP_CODE, number=iters)
    time_zip = timeit.timeit(TEST_ZIP, setup=SETUP_CODE, number=iters)
    
    print(f"  {'Method':<35} {'Time (s) for 100 runs':>20}")
    print("  " + "-" * 56)
    print(f"  {'tuple(v1) == tuple(v2)':<35} {time_tuple:>20.4f}")
    print(f"  {'all(a==b for a,b in zip(v1,v2))':<35} {time_zip:>20.4f}")
    
    speedup = time_tuple / time_zip if time_zip > 0 else 0
    
    print(f"\n  Conclusion: zip+all is {speedup:,.0f}x faster.")
    print("  Why? Tuple conversion allocates two large arrays in memory")
    print("  and scans the whole thing. `zip` paired with `all()`")
    print("  short-circuits and stops at the 5th element early.")

if __name__ == "__main__":
    run_benchmarks()
