"""
Chapter 8: Exercises — Type Hints in Functions
==============================================
Original exercises exploring gradual typing, ABCs, and type constraints.
"""

import sys
from collections import abc
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: Postel's Law in Action
# ─────────────────────────────────────────────────────────────────────────────
# Fix the signature of `process_config` so it accepts ANY mapping 
# (e.g., dict, defaultdict, ChainMap) rather than just `dict`. 
# It should return a concrete `list` of strings.

def process_config(config: abc.Mapping[str, Any]) -> list[str]:
    # Note: Signature updated from `config: dict[str, Any]` to `abc.Mapping`
    return [f"{k}={v}" for k, v in config.items()]

def test_ex1_postel() -> None:
    section("Exercise 1: Postel's Law")
    
    from collections import ChainMap
    d1 = {"host": "localhost"}
    d2 = {"port": 8080}
    cm = ChainMap(d1, d2)
    
    # If the signature required `dict`, passing a ChainMap would fail static checks.
    res = process_config(cm)
    print(f"Config processed: {res}")
    assert len(res) == 2, "Exercise 1 failed"
    print("✓ Exercise 1 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Tuples as Records
# ─────────────────────────────────────────────────────────────────────────────
# Annotate the function `calculate_distance` to accept a `tuple` acting as a record 
# containing `(str, float, float)` representing `(City, Lat, Lon)`.
# Return a float.

def calculate_distance(city1: tuple[str, float, float], city2: tuple[str, float, float]) -> float:
    # Simplified mock distance logic for demonstration
    _, lat1, lon1 = city1
    _, lat2, lon2 = city2
    return abs(lat1 - lat2) + abs(lon1 - lon2)

def test_ex2_records() -> None:
    section("Exercise 2: Tuples as Records")
    
    nyc = ("New York", 40.7128, -74.0060)
    lon = ("London", 51.5074, -0.1278)
    
    dist = calculate_distance(nyc, lon)
    print(f"Mock distance: {dist:.2f}")
    assert dist > 0, "Exercise 2 failed"
    print("✓ Exercise 2 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 3: Python 3.10 Union and Optional Types
# ─────────────────────────────────────────────────────────────────────────────
# Write a function `safe_divide` that takes two `int` parameters.
# If the denominator is 0, return None. Otherwise return a `float`.
# Annotate it using the `|` syntax.

def safe_divide(a: int, b: int) -> float | None:
    if b == 0:
        return None
    return a / b

def test_ex3_union() -> None:
    section("Exercise 3: Union and Optional")
    
    res1 = safe_divide(10, 2)
    res2 = safe_divide(10, 0)
    
    print(f"10 / 2 = {res1}")
    print(f"10 / 0 = {res2}")
    
    assert res1 == 5.0 and res2 is None, "Exercise 3 failed"
    print("✓ Exercise 3 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 4: Immutable Sequence Type Hinting
# ─────────────────────────────────────────────────────────────────────────────
# Write a function `average_scores` that takes a variable-length tuple of floats.
# It should return a float. Annotate it correctly.

def average_scores(scores: tuple[float, ...]) -> float:
    if not scores:
        return 0.0
    return sum(scores) / len(scores)

def test_ex4_sequences() -> None:
    section("Exercise 4: Immutable Sequences")
    
    res = average_scores((90.5, 80.0, 100.0))
    print(f"Average: {res:.1f}")
    assert 90.0 < res < 91.0, "Exercise 4 failed"
    print("✓ Exercise 4 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 5: Any vs object
# ─────────────────────────────────────────────────────────────────────────────
# Show the difference between `Any` and `object`.
# `Any` assumes all operations are valid. `object` assumes almost none are.

def double_any(x: Any) -> Any:
    return x * 2  # Mypy allows this

def double_object(x: object) -> object:
    # return x * 2  # Mypy strictly forbids this: Unsupported operand types for *
    # We must return something safe for object, or just bypass it for the exercise.
    return x

def test_ex5_any_vs_object() -> None:
    section("Exercise 5: Any vs object")
    
    res_any = double_any(10)
    res_obj = double_object(10)
    
    print(f"double_any(10) -> {res_any} (Mypy trusts you)")
    print(f"double_object(10) -> {res_obj} (Mypy restricts operations)")
    
    assert res_any == 20, "Exercise 5 failed"
    print("✓ Exercise 5 passed")


if __name__ == "__main__":
    test_ex1_postel()
    test_ex2_records()
    test_ex3_union()
    test_ex4_sequences()
    test_ex5_any_vs_object()
