"""
Chapter 24: Benchmarks — Import Time vs Execution Time
======================================================
Metaclasses do heavy lifting, but the significant advantage of metaprogramming
is that the cost is paid at IMPORT time (Evaluation Time), not RUNTIME.

This benchmark proves that once a class is built by a metaclass,
accessing it is literally just as fast as a normal class.
"""

import sys
import timeit

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Setup ────────────────────────────────────────────────────────────────────

SETUP_CODE = """
class NormalClass:
    data = 42

class HeavyMeta(type):
    def __new__(meta, name, bases, dic):
        # Simulate heavy validation/processing during class creation
        x = sum(i * i for i in range(1000))
        dic['data'] = 42
        return super().__new__(meta, name, bases, dic)

class MetaClass(metaclass=HeavyMeta):
    pass

obj_normal = NormalClass()
obj_meta = MetaClass()
"""

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark: Metaclass Runtime Penalty")
    
    iters = 10_000_000
    print(f"  (Executing {iters:,} attribute accesses)\n")
    
    # We are benchmarking EXECUTION time.
    time_normal = timeit.timeit("x = obj_normal.data", setup=SETUP_CODE, number=iters)
    time_meta = timeit.timeit("x = obj_meta.data", setup=SETUP_CODE, number=iters)
    
    print(f"  {'Class Type':<20} {'Time (s)':>12}")
    print("  " + "-" * 33)
    print(f"  {'Normal Class':<20} {time_normal:>12.4f}")
    print(f"  {'Metaclass Built':<20} {time_meta:>12.4f}")
    
    print("\n  Conclusion:")
    print("  The execution times are virtually identical.")
    print("  Metaclasses are 'free' at runtime because all the heavy")
    print("  validation and generation happens exactly once, when the")
    print("  module is first imported by Python.")

if __name__ == "__main__":
    run_benchmarks()
