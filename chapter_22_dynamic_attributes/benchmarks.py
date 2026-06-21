"""
Chapter 22: Benchmarks — The Cost of Metaprogramming
====================================================
Dynamic attributes (`__getattr__`) and properties (`@property`) are
beautiful, but they execute Python bytecodes every time they are accessed.
Raw dictionary/attribute access does not. This benchmark measures the 
speed penalty of dynamic abstraction.
"""

import sys
import timeit

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Setup ────────────────────────────────────────────────────────────────────

SETUP_CODE = """
class RawObject:
    def __init__(self, data):
        self.value = data

class PropertyObject:
    def __init__(self, data):
        self._value = data
    @property
    def value(self):
        return self._value

class DynamicObject:
    def __init__(self, data):
        self.__data = {"value": data}
    def __getattr__(self, name):
        return self.__data[name]

raw_dict = {"value": 42}
obj_raw = RawObject(42)
obj_prop = PropertyObject(42)
obj_dyn = DynamicObject(42)
"""

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark: Attribute Access Speed")
    
    iters = 10_000_000
    print(f"  (Executing {iters:,} access operations)\n")
    
    time_dict = timeit.timeit("x = raw_dict['value']", setup=SETUP_CODE, number=iters)
    time_raw = timeit.timeit("x = obj_raw.value", setup=SETUP_CODE, number=iters)
    time_prop = timeit.timeit("x = obj_prop.value", setup=SETUP_CODE, number=iters)
    time_dyn = timeit.timeit("x = obj_dyn.value", setup=SETUP_CODE, number=iters)
    
    print(f"  {'Access Method':<25} {'Time (s)':>12}")
    print("  " + "-" * 38)
    print(f"  {'Raw Dictionary [key]':<25} {time_dict:>12.4f}")
    print(f"  {'Raw Attribute (obj.x)':<25} {time_raw:>12.4f}")
    print(f"  {'Property (@property)':<25} {time_prop:>12.4f}")
    print(f"  {'Dynamic (__getattr__)':<25} {time_dyn:>12.4f}")
    
    print("\n  Conclusion:")
    print("  Raw attribute access is the fastest.")
    print("  @property adds overhead because it invokes a method call.")
    print("  __getattr__ is the slowest because Python must fail the")
    print("  standard lookup, catch the miss, and execute __getattr__.")
    print("  Rule of thumb: Metaprogramming costs ~2x-3x access speed.")

if __name__ == "__main__":
    run_benchmarks()
