"""
Chapter 14: Benchmarks — The Cost of Safe Subclassing
=====================================================
Subclassing `collections.UserDict` is safer than subclassing `dict` because 
it routes all internal calls through Python. But what is the performance cost 
of bypassing the highly optimized C-layer?
"""

import sys
import timeit
from collections import UserDict

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Setup ────────────────────────────────────────────────────────────────────

SETUP_CODE = """
from collections import UserDict

class NativeDict(dict):
    pass

class SafeDict(UserDict):
    pass

native = NativeDict()
safe = SafeDict()

data = {f"key{i}": i for i in range(1000)}
"""

# Native `dict.update` (executes in C)
TEST_NATIVE = "native.update(data)"

# `UserDict.update` (executes in Python, triggering Python assignments)
TEST_SAFE = "safe.update(data)"

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark: `dict` vs `UserDict` write speeds")
    
    iters = 10_000
    print(f"  (Running .update() with 1000 items, {iters:,} times)\n")
    
    time_native = timeit.timeit(TEST_NATIVE, setup=SETUP_CODE, number=iters)
    time_safe = timeit.timeit(TEST_SAFE, setup=SETUP_CODE, number=iters)
    
    print(f"  {'Method':<35} {'Time (s)':>15}")
    print("  " + "-" * 51)
    print(f"  {'NativeDict.update (C-level)':<35} {time_native:>15.4f}")
    print(f"  {'SafeDict.update (Python-level)':<35} {time_safe:>15.4f}")
    
    slower = time_safe / time_native if time_native > 0 else 0
    
    print(f"\n  Conclusion: UserDict is ~{slower:.1f}x slower for bulk writes.")
    print("  Why? `UserDict` forces every single assignment to jump from")
    print("  the C layer back into the Python evaluation loop, ensuring")
    print("  your overridden __setitem__ is respected. Native dict updates")
    print("  happen entirely in C, bypassing Python logic entirely.")

if __name__ == "__main__":
    run_benchmarks()
