"""
Chapter 18: Benchmarks — EAFP vs LBYL
=====================================
Comparing "Easier to Ask Forgiveness than Permission" (try/except)
vs "Look Before You Leap" (if/else).
"""

import sys
import timeit

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Setup ────────────────────────────────────────────────────────────────────

SETUP_CODE = """
import random
data_valid = {"key": "value"}
data_invalid = {}
"""

# EAFP (Easier to Ask Forgiveness than Permission)
TEST_EAFP_HAPPY = """
try:
    x = data_valid["key"]
except KeyError:
    x = None
"""

TEST_EAFP_SAD = """
try:
    x = data_invalid["key"]
except KeyError:
    x = None
"""

# LBYL (Look Before You Leap)
TEST_LBYL_HAPPY = """
if "key" in data_valid:
    x = data_valid["key"]
else:
    x = None
"""

TEST_LBYL_SAD = """
if "key" in data_invalid:
    x = data_invalid["key"]
else:
    x = None
"""

# ── Benchmarks ───────────────────────────────────────────────────────────────

def run_benchmarks():
    section("Benchmark: EAFP (try) vs LBYL (if)")
    
    iters = 10_000_000
    print(f"  (Executing dictionary lookups {iters:,} times)\n")
    
    # Happy Path (Key exists)
    time_eafp_happy = timeit.timeit(TEST_EAFP_HAPPY, setup=SETUP_CODE, number=iters)
    time_lbyl_happy = timeit.timeit(TEST_LBYL_HAPPY, setup=SETUP_CODE, number=iters)
    
    # Sad Path (Key missing)
    time_eafp_sad = timeit.timeit(TEST_EAFP_SAD, setup=SETUP_CODE, number=iters)
    time_lbyl_sad = timeit.timeit(TEST_LBYL_SAD, setup=SETUP_CODE, number=iters)
    
    print(f"  {'Scenario':<25} {'EAFP (s)':>12} {'LBYL (s)':>12}")
    print("  " + "-" * 51)
    print(f"  {'Happy Path (Success)':<25} {time_eafp_happy:>12.4f} {time_lbyl_happy:>12.4f}")
    print(f"  {'Sad Path (Exception)':<25} {time_eafp_sad:>12.4f} {time_lbyl_sad:>12.4f}")
    
    print("\n  Conclusion:")
    print("  When the key exists (Happy Path), EAFP (try/except) is faster because it")
    print("  does 1 lookup instead of 2 (checking 'in' then getting the value).")
    print("  However, when the key is missing (Sad Path), raising an exception is")
    print("  highly expensive, making EAFP much slower.")
    print("\n  Rule of thumb: Use EAFP if exceptions are truly rare. Use LBYL if")
    print("  missing data is extremely common.")

if __name__ == "__main__":
    run_benchmarks()
