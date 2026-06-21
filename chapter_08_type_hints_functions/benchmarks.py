"""
Chapter 8: Benchmarks — Type Introspection Overhead
===================================================
Measures the runtime overhead of parsing type annotations using `get_type_hints`.
Run: python benchmarks.py
"""

import sys
import timeit
from typing import get_type_hints

sys.stdout.reconfigure(encoding="utf-8")

N = 10_000

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

def measure(stmt: str, setup: str, n: int = N) -> float:
    return (timeit.timeit(stmt, setup=setup, number=n) * 1000)


section("Benchmark 1: Overhead of get_type_hints")
print(f"  (Resolving annotations {N} times)")

setup_code = """
import typing
from typing import get_type_hints

def complex_func(
    a: int, 
    b: str, 
    c: list[typing.Any], 
    d: dict[str, tuple[int, float]]
) -> typing.Optional[bool]:
    pass

# __annotations__ is the raw dict generated at compile time
raw_annotations = complex_func.__annotations__
"""

# Accessing raw __annotations__ is an O(1) dictionary lookup
stmt_raw = "complex_func.__annotations__"

# get_type_hints has to resolve forward references, process stringified annotations, 
# and handle inheritance in classes.
stmt_resolve = "get_type_hints(complex_func)"

t_raw = measure(stmt_raw, setup_code)
t_resolve = measure(stmt_resolve, setup_code)

print(f"  {'Operation':<35} {'Time (ms)':>12}")
print("  " + "-" * 48)
print(f"  {'.__annotations__ lookup':<35} {t_raw:>12.2f}")
print(f"  {'typing.get_type_hints()':<35} {t_resolve:>12.2f}")

print("""
  Conclusion: Accessing `__annotations__` directly is incredibly fast because 
  it's a simple dictionary lookup. However, frameworks like Pydantic or FastAPI 
  must use `get_type_hints` to safely resolve stringified annotations (PEP 563) 
  and forward references, which introduces noticeable runtime overhead.
""")
