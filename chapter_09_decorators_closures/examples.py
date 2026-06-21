"""
Chapter 9: Decorators and Closures
==================================
Original implementations exploring Python closures and decorators.

Key concepts covered:
- Decorator execution time (import vs runtime)
- Closures and the `nonlocal` declaration
- Building a well-behaved decorator with `functools.wraps`
- Standard library decorators (`lru_cache`, `singledispatch`)
- Parameterized decorators
"""

import sys
import time
import functools
import html
import numbers
from collections import abc
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Part 1: Decorators Execute at Import Time
# ─────────────────────────────────────────────────────────────────────────────

registry = []

def register(func):
    """A decorator that simply adds the function to a registry list."""
    # This print happens as soon as the module is evaluated!
    print(f"running register({func.__name__})")
    registry.append(func)
    return func

@register
def f1():
    print("running f1()")

@register
def f2():
    print("running f2()")

def f3():
    print("running f3()")

def demo_registration() -> None:
    section("Part 1: Decorator Execution Time")
    print("running main()")
    print("registry ->", [f.__name__ for f in registry])
    f1()
    f2()
    f3()


# ─────────────────────────────────────────────────────────────────────────────
# Part 2: Closures and `nonlocal`
# ─────────────────────────────────────────────────────────────────────────────
# A closure retains bindings of free variables that exist when the function 
# is defined, so they can be used later when the function is invoked.

def make_averager():
    """A high-order function returning a closure that computes a running average."""
    count = 0
    total = 0.0

    def averager(new_value: float) -> float:
        # `count` and `total` are "free variables" in this inner function.
        # Without `nonlocal`, assigning to them would create local variables,
        # shadowing the free variables and raising an UnboundLocalError.
        nonlocal count, total
        count += 1
        total += new_value
        return total / count

    return averager

def demo_closures() -> None:
    section("Part 2: Closures and `nonlocal`")
    avg = make_averager()
    print(f"avg(10) -> {avg(10)}")
    print(f"avg(11) -> {avg(11)}")
    print(f"avg(12) -> {avg(12)}")
    
    # Inspecting the closure
    print("\nInspecting the closure __closure__ attribute:")
    for i, cell in enumerate(avg.__closure__):
        print(f"  Cell {i} contents: {cell.cell_contents}")


# ─────────────────────────────────────────────────────────────────────────────
# Part 3: A Proper Custom Decorator
# ─────────────────────────────────────────────────────────────────────────────

def clock(func):
    """A decorator that prints the execution time of the decorated function."""
    
    # wraps preserves metadata like __name__ and __doc__ of the original func
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.perf_counter()
        
        # Call the original function
        result = func(*args, **kwargs)
        
        elapsed = time.perf_counter() - t0
        name = func.__name__
        arg_lst = [repr(arg) for arg in args]
        arg_lst.extend(f"{k}={v!r}" for k, v in kwargs.items())
        arg_str = ", ".join(arg_lst)
        print(f"[{elapsed:0.5f}s] {name}({arg_str}) -> {result!r}")
        return result
        
    return clocked

@clock
def snooze(seconds: float):
    time.sleep(seconds)

def demo_clock() -> None:
    section("Part 3: Custom Decorators (@clock)")
    print("Calling snooze(0.123)...")
    snooze(0.123)
    print(f"snooze.__name__ is {snooze.__name__!r} (thanks to @wraps)")


# ─────────────────────────────────────────────────────────────────────────────
# Part 4: Standard Library: @lru_cache and @singledispatch
# ─────────────────────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=128)
@clock
def fibonacci(n: int) -> int:
    """Computes nth Fibonacci number using recursion and memoization."""
    if n < 2:
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)

@functools.singledispatch
def htmlize(obj: Any) -> str:
    """Generates HTML representation. Defaults to string escaping."""
    content = html.escape(repr(obj))
    return f"<pre>{content}</pre>"

@htmlize.register(str)
def _(text: str) -> str:
    content = html.escape(text).replace("\n", "<br>\n")
    return f"<p>{content}</p>"

@htmlize.register(numbers.Integral)
def _(n: int) -> str:
    return f"<pre>{n} (0x{n:x})</pre>"

def demo_stdlib_decorators() -> None:
    section("Part 4: Stdlib (@lru_cache & @singledispatch)")
    print("Computing fibonacci(6) with lru_cache:")
    fibonacci(6)
    
    print("\nhtmlize singledispatch:")
    print(htmlize({1, 2, 3}))  # Default fallback
    print(htmlize(42))         # Integral
    print(htmlize("He & She")) # String


# ─────────────────────────────────────────────────────────────────────────────
# Part 5: Parameterized Decorators
# ─────────────────────────────────────────────────────────────────────────────

def html_tag(tag: str):
    """A decorator factory that creates decorators parameterized by tag."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return f"<{tag}>{result}</{tag}>"
        return wrapper
    return decorator

@html_tag("strong")
def emphasize(text: str) -> str:
    return text.upper()

def demo_parameterized() -> None:
    section("Part 5: Parameterized Decorators")
    print(f"emphasize('hello') -> {emphasize('hello')}")


if __name__ == "__main__":
    demo_registration()
    demo_closures()
    demo_clock()
    demo_stdlib_decorators()
    demo_parameterized()
