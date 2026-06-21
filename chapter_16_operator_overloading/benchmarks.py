"""
Chapter 16: Benchmarks — In-Place Mutation vs Object Creation
=============================================================
Comparing `__iadd__` (which mutates internal state) vs `__add__`
(which forces `a = a + b` object creation) for mathematical operations.
"""

import sys
import timeit
from array import array

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Setup ────────────────────────────────────────────────────────────────────

SETUP_CODE = """
class FastWallet:
    def __init__(self, val):
        self.val = val
    def __iadd__(self, other):
        self.val += other.val
        return self

class SlowWallet:
    def __init__(self, val):
        self.val = val
    def __add__(self, other):
        # Creates a brand new object every time
        return SlowWallet(self.val + other.val)

fast = FastWallet(0)
slow = SlowWallet(0)

amount = FastWallet(10)
amount_slow = SlowWallet(10)
"""

TEST_IN_PLACE = """
fast += amount
"""

TEST_FALLBACK = """
slow += amount_slow
"""

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark: __iadd__ vs __add__ Fallback")
    
    iters = 2_000_000
    print(f"  (Executing `wallet += amount` {iters:,} times)\n")
    
    time_inplace = timeit.timeit(TEST_IN_PLACE, setup=SETUP_CODE, number=iters)
    time_fallback = timeit.timeit(TEST_FALLBACK, setup=SETUP_CODE, number=iters)
    
    print(f"  {'Method':<35} {'Time (s)':>15}")
    print("  " + "-" * 51)
    print(f"  {'__iadd__ (Mutates self)':<35} {time_inplace:>15.4f}")
    print(f"  {'__add__ (Allocates new object)':<35} {time_fallback:>15.4f}")
    
    slower = time_fallback / time_inplace if time_inplace > 0 else 0
    
    print(f"\n  Conclusion: Falling back to object creation is ~{slower:.1f}x slower.")
    print("  If your objects wrap heavy data structures (like arrays or tensors),")
    print("  you MUST implement __iadd__ to avoid severe memory thrashing.")

if __name__ == "__main__":
    run_benchmarks()
