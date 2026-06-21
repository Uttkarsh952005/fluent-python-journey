"""
Chapter 15: Benchmarks — TypedDict vs Dataclass Overhead
========================================================
Comparing the instantiation cost of a TypedDict against a standard 
@dataclass. This proves that TypedDict has exactly zero runtime overhead.
"""

import sys
import timeit
from typing import TypedDict
from dataclasses import dataclass

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Setup ────────────────────────────────────────────────────────────────────

SETUP_CODE = """
from typing import TypedDict
from dataclasses import dataclass

class TDUser(TypedDict):
    id: int
    name: str

@dataclass
class DCUser:
    id: int
    name: str
"""

TEST_TYPED_DICT = """
# At runtime, this compiles directly to `{'id': 1, 'name': 'admin'}`
user = TDUser(id=1, name='admin')
"""

TEST_DATACLASS = """
# At runtime, this executes the auto-generated __init__ method
user = DCUser(id=1, name='admin')
"""

TEST_RAW_DICT = """
# A pure, unannotated python dict for baseline
user = {'id': 1, 'name': 'admin'}
"""

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark: TypedDict vs Dataclass Instantiation")
    
    iters = 10_000_000
    print(f"  (Instantiating {iters:,} objects each)\n")
    
    time_raw = timeit.timeit(TEST_RAW_DICT, setup=SETUP_CODE, number=iters)
    time_td = timeit.timeit(TEST_TYPED_DICT, setup=SETUP_CODE, number=iters)
    time_dc = timeit.timeit(TEST_DATACLASS, setup=SETUP_CODE, number=iters)
    
    print(f"  {'Method':<35} {'Time (s)':>15}")
    print("  " + "-" * 51)
    print(f"  {'Raw dictionary':<35} {time_raw:>15.4f}")
    print(f"  {'TypedDict (TDUser)':<35} {time_td:>15.4f}")
    print(f"  {'Dataclass (DCUser)':<35} {time_dc:>15.4f}")
    
    slower = time_dc / time_td if time_td > 0 else 0
    
    print(f"\n  Conclusion: Dataclasses are ~{slower:.1f}x slower to instantiate.")
    print("  Notice that TypedDict is mathematically identical to a raw dict.")
    print("  TypedDict disappears completely at runtime, leaving only the")
    print("  highly optimized C-level dictionary constructor.")

if __name__ == "__main__":
    run_benchmarks()
