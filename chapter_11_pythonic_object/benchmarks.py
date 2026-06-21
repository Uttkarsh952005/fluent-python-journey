"""
Chapter 11: Benchmarks — The Memory Savings of __slots__
========================================================
Measures the RAM footprint of 1,000,000 objects with and without __slots__.
Run: python benchmarks.py
"""

import sys
import tracemalloc

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Setup Classes ────────────────────────────────────────────────────────────

class DictPoint:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

class SlotPoint:
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

# ── Benchmarks ───────────────────────────────────────────────────────────────

def measure_memory(cls, num_instances: int) -> float:
    tracemalloc.start()
    
    # Store in a list so they aren't garbage collected
    instances = [cls(1.0, 2.0, 3.0) for _ in range(num_instances)]
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Return memory used in Megabytes
    return peak / (1024 * 1024)

def run_benchmarks():
    section("Benchmark 1: __dict__ vs __slots__ Memory Footprint")
    
    N = 1_000_000
    print(f"  (Allocating {N:,} instances of a 3-dimensional Point)\n")
    
    mem_dict = measure_memory(DictPoint, N)
    mem_slots = measure_memory(SlotPoint, N)
    
    print(f"  {'Architecture':<35} {'Memory Used (MB)':>16}")
    print("  " + "-" * 52)
    print(f"  {'Standard class (uses __dict__)':<35} {mem_dict:>16.2f}")
    print(f"  {'Optimized class (uses __slots__)':<35} {mem_slots:>16.2f}")
    
    savings = mem_dict - mem_slots
    ratio = mem_dict / mem_slots if mem_slots > 0 else 0
    
    print(f"\n  Conclusion: __slots__ saved ~{savings:.1f} MB.")
    print(f"  The standard class uses roughly {ratio:.1f}x more memory because")
    print(f"  every single instance must allocate a dynamic hash table")
    print(f"  (dictionary) to store its attributes.")

if __name__ == "__main__":
    run_benchmarks()
