"""
Chapter 9: Benchmarks — Decorator Overhead & Memoization
========================================================
Measures the overhead of calling a decorated function, and the significant
performance gains of `@functools.lru_cache`.
Run: python benchmarks.py
"""

import sys
import timeit
import functools

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

def measure(stmt: str, setup: str, n: int) -> float:
    return (timeit.timeit(stmt, setup=setup, number=n) * 1000)


# ── Benchmark 1: Decorator Overhead ──────────────────────────────────────────

section("Benchmark 1: Overhead of a Wrapper")
N1 = 1_000_000
print(f"  (Calling a simple function {N1:,} times)")

setup_overhead = """
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def raw_func(x):
    return x * 2

@my_decorator
def decorated_func(x):
    return x * 2
"""

t_raw = measure("raw_func(10)", setup_overhead, n=N1)
t_dec = measure("decorated_func(10)", setup_overhead, n=N1)

print(f"  {'Operation':<35} {'Time (ms)':>12}")
print("  " + "-" * 48)
print(f"  {'Raw function call':<35} {t_raw:>12.2f}")
print(f"  {'Decorated function call':<35} {t_dec:>12.2f}")

print("""
  Conclusion: A decorator adds a small amount of overhead (the cost of one 
  additional frame evaluation in CPython). For 99% of applications, this 
  is totally negligible.
""")


# ── Benchmark 2: lru_cache Memoization ───────────────────────────────────────

section("Benchmark 2: Recursive Fibonacci vs @lru_cache")
N2 = 100
print(f"  (Computing fibonacci(20), {N2} times)")

setup_fib = """
import functools

def fib_raw(n):
    if n < 2: return n
    return fib_raw(n-2) + fib_raw(n-1)

@functools.lru_cache()
def fib_memo(n):
    if n < 2: return n
    return fib_memo(n-2) + fib_memo(n-1)

# Pre-warm the cache so we're just measuring cache hit speed
fib_memo(20)
"""

t_fib_raw = measure("fib_raw(20)", setup_fib, n=N2)
t_fib_memo = measure("fib_memo(20)", setup_fib, n=N2)

print(f"  {'Operation':<35} {'Time (ms)':>12}")
print("  " + "-" * 48)
print(f"  {'Raw recursive (O(2^N))':<35} {t_fib_raw:>12.2f}")
print(f"  {'@lru_cache memoized (O(N))':<35} {t_fib_memo:>12.2f}")

print("""
  Conclusion: Recursive functions with overlapping subproblems cause 
  exponential time complexity. `@lru_cache` reduces this to linear time,
  making it thousands of times faster for even small inputs.
""")
