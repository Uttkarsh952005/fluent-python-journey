"""
Chapter 13: Benchmarks — Duck Typing vs Goose Typing (isinstance)
=================================================================
Comparing the runtime cost of checking for an attribute (Duck typing)
vs using isinstance() against an Abstract Base Class (Goose typing).
"""

import sys
import timeit
import collections.abc

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Setup ────────────────────────────────────────────────────────────────────

SETUP_CODE = """
import collections.abc

class DuckSequence:
    def __len__(self): return 0
    def __getitem__(self, i): raise IndexError

class GooseSequence(collections.abc.Sequence):
    def __len__(self): return 0
    def __getitem__(self, i): raise IndexError

duck = DuckSequence()
goose = GooseSequence()
"""

# Duck typing: "Does it have a __len__?"
TEST_DUCK = """
has_len = hasattr(duck, '__len__')
"""

# Goose typing: "Is it an instance of Sequence?"
TEST_GOOSE = """
is_seq = isinstance(goose, collections.abc.Sequence)
"""

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark: hasattr() vs isinstance(ABC)")
    
    iters = 5_000_000
    print(f"  (Running {iters:,} iterations each)\n")
    
    time_duck = timeit.timeit(TEST_DUCK, setup=SETUP_CODE, number=iters)
    time_goose = timeit.timeit(TEST_GOOSE, setup=SETUP_CODE, number=iters)
    
    print(f"  {'Method':<35} {'Time (s)':>15}")
    print("  " + "-" * 51)
    print(f"  {'Duck: hasattr(obj, __len__)':<35} {time_duck:>15.4f}")
    print(f"  {'Goose: isinstance(obj, Sequence)':<35} {time_goose:>15.4f}")
    
    slower = time_goose / time_duck if time_duck > 0 else 0
    
    print(f"\n  Conclusion: isinstance() against an ABC is ~{slower:.1f}x slower.")
    print("  Why? `hasattr` is a direct dictionary lookup on the C struct.")
    print("  `isinstance` against an ABC must traverse the MRO, invoke")
    print("  the ABCMeta metaclass, and often execute __subclasshook__.")

if __name__ == "__main__":
    run_benchmarks()
