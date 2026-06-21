"""
Chapter 17: Exercises — Generator Exhaustion and Priming
========================================================
Original exercises demonstrating the two most common traps when 
working with generators and coroutines.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Generator Exhaustion Trap
# ─────────────────────────────────────────────────────────────────────────────
# Standard iterables (like lists) can be looped over infinitely. 
# Generators CANNOT. Once they yield their values, they are exhausted forever.

def test_ex1_exhaustion() -> None:
    section("Exercise 1: Generator Exhaustion")
    
    # Create a generator expression
    gen = (x * 2 for x in range(3))
    
    # First loop: consumes the generator
    list_1 = list(gen)
    print(f"First pass: {list_1}")
    
    # Second loop: the generator is already exhausted!
    list_2 = list(gen)
    print(f"Second pass: {list_2}")
    
    assert list_1 == [0, 2, 4]
    assert list_2 == [], "Generator should be empty on the second pass!"
    print("✓ Exercise 1 passed: Proved generators are strictly single-use.")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: The Unprimed Coroutine
# ─────────────────────────────────────────────────────────────────────────────
# You cannot send data into a coroutine until you have "primed" it by
# advancing it to the very first `yield` expression.

def simple_coroutine():
    print("  -> Coroutine started")
    x = yield
    print(f"  -> Coroutine received: {x}")

def test_ex2_priming() -> None:
    section("Exercise 2: The Priming Trap")
    
    coro = simple_coroutine()
    
    try:
        # BUG: We forgot to call next(coro) first!
        coro.send("Hello")
        assert False, "Should have raised TypeError"
    except TypeError as e:
        print(f"Caught failure: {e}")
        print("✓ Exercise 2 passed: Proved you cannot send data into an unprimed coroutine.")


if __name__ == "__main__":
    test_ex1_exhaustion()
    test_ex2_priming()
