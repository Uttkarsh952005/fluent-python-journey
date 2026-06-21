"""
Chapter 7: Benchmarks — First-Class Functions
=============================================
Measures the overhead of different functional programming patterns.
Run: python benchmarks.py
"""

import sys
import timeit
from functools import partial

sys.stdout.reconfigure(encoding="utf-8")

N = 100_000

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

def measure(stmt: str, setup: str, n: int = N) -> float:
    # return milliseconds per iteration of the whole setup (or nanoseconds per op)
    # We will output total time for N operations in ms
    return (timeit.timeit(stmt, setup=setup, number=n) * 1000)


# ── Benchmark 1: map/filter vs List Comprehension ────────────────────────────

section("Benchmark 1: map/filter vs List Comprehension")
print(f"  (Processing {N} lists of 100 integers)")

setup_data = """
data = list(range(100))
def square(x): return x * x
def is_even(x): return x % 2 == 0
"""

# map + filter with predefined functions
stmt_map_filter = "list(map(square, filter(is_even, data)))"

# map + filter with lambda (often slower due to lambda dispatch overhead)
stmt_map_lambda = "list(map(lambda x: x*x, filter(lambda x: x%2==0, data)))"

# list comprehension
stmt_listcomp = "[x * x for x in data if x % 2 == 0]"

t_map_filter = measure(stmt_map_filter, setup_data)
t_map_lambda = measure(stmt_map_lambda, setup_data)
t_listcomp   = measure(stmt_listcomp, setup_data)

print(f"  {'Operation':<35} {'Time (ms)':>12}")
print("  " + "-" * 48)
print(f"  {'map + filter (named funcs)':<35} {t_map_filter:>12.2f}")
print(f"  {'map + filter (lambdas)':<35} {t_map_lambda:>12.2f}")
print(f"  {'list comprehension':<35} {t_listcomp:>12.2f}")

print("""
  Conclusion: List comprehensions are generally faster and more readable 
  than map/filter, especially when lambdas are involved. The overhead of 
  calling a Python function (lambda) inside the tight C-loop of map/filter 
  is significant.
""")


# ── Benchmark 2: functools.partial vs lambda vs def ──────────────────────────

section("Benchmark 2: functools.partial vs lambda")
print(f"  (Executing a frozen argument wrapper {N*10} times)")

setup_partial = """
from functools import partial
def multiply(a, b): return a * b
triple_partial = partial(multiply, 3)
triple_lambda = lambda x: multiply(3, x)
def triple_def(x): return multiply(3, x)
"""

n_calls = N * 10
t_partial = measure("triple_partial(7)", setup_partial, n=n_calls)
t_lambda  = measure("triple_lambda(7)", setup_partial, n=n_calls)
t_def     = measure("triple_def(7)", setup_partial, n=n_calls)

print(f"  {'Operation':<35} {'Time (ms)':>12}")
print("  " + "-" * 48)
print(f"  {'functools.partial':<35} {t_partial:>12.2f}")
print(f"  {'lambda wrapper':<35} {t_lambda:>12.2f}")
print(f"  {'def wrapper':<35} {t_def:>12.2f}")

print("""
  Conclusion: functools.partial is implemented in C and heavily optimized. 
  It usually performs similarly to or slightly better than a def/lambda wrapper, 
  with the added benefit of preserving metadata better than lambdas.
""")


# ── Benchmark 3: itemgetter vs lambda ────────────────────────────────────────

section("Benchmark 3: itemgetter vs lambda for sorting")
print(f"  (Sorting a list of 1000 tuples, {N//10} times)")

setup_sort = """
from operator import itemgetter
import random
data = [(random.random(), i) for i in range(1000)]
get_item = itemgetter(1)
get_lambda = lambda x: x[1]
"""

n_sorts = N // 10
t_itemgetter = measure("sorted(data, key=get_item)", setup_sort, n=n_sorts)
t_lambda_sort = measure("sorted(data, key=get_lambda)", setup_sort, n=n_sorts)

print(f"  {'Operation':<35} {'Time (ms)':>12}")
print("  " + "-" * 48)
print(f"  {'operator.itemgetter':<35} {t_itemgetter:>12.2f}")
print(f"  {'lambda':<35} {t_lambda_sort:>12.2f}")

print("""
  Conclusion: operator.itemgetter is written in C. When passed to C-level 
  functions like sorted(), it skips the bytecode evaluation loop entirely, 
  making it noticeably faster than an equivalent lambda.
""")
