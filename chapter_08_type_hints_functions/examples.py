"""
Chapter 8: Type Hints in Functions
==================================
Original implementations exploring gradual typing in Python.

Key concepts demonstrated:
- Duck typing vs Nominal typing
- Using Abstract Base Classes (ABCs) for liberal parameter acceptance
- Tuples as immutable sequences vs records
- The `Any` type and `Optional` / `Union` (Python 3.10+ syntax `|`)
"""

import sys
from collections import abc
from typing import Any, NamedTuple

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Part 1: Duck Typing vs Nominal Typing
# ─────────────────────────────────────────────────────────────────────────────
# In duck typing, the type checker ignores the signature and Python executes
# based on supported methods. In nominal typing, Mypy enforces the named type.

class Bird:
    pass

class Duck(Bird):
    def quack(self) -> str:
        return "Quack!"

# Duck-typed function (no type hints, Mypy ignores this)
def alert_duck_typed(birdie):
    return birdie.quack()

# Nominally-typed function (Mypy will flag an error if called with just a Bird)
def alert_nominally_typed(birdie: Duck) -> str:
    return birdie.quack()

def demo_duck_vs_nominal() -> None:
    section("Part 1: Duck Typing vs Nominal Typing")
    
    daffy = Duck()
    woody = Bird()
    
    print(f"Duck typed (Daffy): {alert_duck_typed(daffy)}")
    
    try:
        # Fails at runtime, but Mypy couldn't warn us because of no type hints!
        alert_duck_typed(woody)
    except AttributeError as e:
        print(f"Duck typed (Woody) runtime failure: {e}")
        
    print(f"Nominal typed (Daffy): {alert_nominally_typed(daffy)}")
    # If we ran Mypy, it would statically flag: alert_nominally_typed(woody)


# ─────────────────────────────────────────────────────────────────────────────
# Part 2: Postel's Law (Be liberal in what you accept)
# ─────────────────────────────────────────────────────────────────────────────
# Accept ABCs (like abc.Sequence or abc.Mapping) instead of concrete classes
# (like list or dict). Return concrete classes.

# BAD: Requires exactly a `list`. Will fail static checks if given a `tuple`.
def uppercase_list(items: list[str]) -> list[str]:
    return [item.upper() for item in items]

# GOOD: Accepts any Sequence (list, tuple, str). Returns a concrete list.
def uppercase_sequence(items: abc.Sequence[str]) -> list[str]:
    return [item.upper() for item in items]

def demo_postels_law() -> None:
    section("Part 2: Postel's Law (ABCs vs Concrete Types)")
    
    my_list = ["a", "b", "c"]
    my_tuple = ("x", "y", "z")
    
    print(f"List with list:  {uppercase_list(my_list)}")
    # uppercase_list(my_tuple)  # Mypy error: Expected list[str], got tuple[str, ...]
    
    print(f"Seq with list:   {uppercase_sequence(my_list)}")
    print(f"Seq with tuple:  {uppercase_sequence(my_tuple)}  <- Type safe!")


# ─────────────────────────────────────────────────────────────────────────────
# Part 3: Tuples as Records vs Immutable Sequences
# ─────────────────────────────────────────────────────────────────────────────

# Record: Fixed length, specific types per position
Coordinate = tuple[float, float]

def format_coord(coord: Coordinate) -> str:
    lat, lon = coord
    return f"{abs(lat):.1f}°{'N' if lat >= 0 else 'S'}, {abs(lon):.1f}°{'E' if lon >= 0 else 'W'}"

# Immutable Sequence: Variable length, single type
def summarize_scores(scores: tuple[int, ...]) -> str:
    return f"Count: {len(scores)}, Max: {max(scores) if scores else 0}"

def demo_tuple_types() -> None:
    section("Part 3: Tuple Type Hints")
    
    tokyo = (35.6895, 139.6917)
    print(f"Record (Coordinate): {format_coord(tokyo)}")
    
    game_scores = (10, 50, 100, 20)
    print(f"Sequence (tuple[int, ...]): {summarize_scores(game_scores)}")


# ─────────────────────────────────────────────────────────────────────────────
# Part 4: Optional and Union (Python 3.10+ | syntax)
# ─────────────────────────────────────────────────────────────────────────────

def show_count(count: int, singular: str, plural: str | None = None) -> str:
    """Uses Python 3.10+ union operator `|` for Optional types."""
    if count == 1:
        return f"1 {singular}"
    
    count_str = str(count) if count else "no"
    if not plural:
        plural = singular + "s"
        
    return f"{count_str} {plural}"

def parse_token(token: str) -> str | float:
    """May return a string or a float."""
    try:
        return float(token)
    except ValueError:
        return token

def demo_unions() -> None:
    section("Part 4: Union and Optional")
    
    print(f"show_count(1, 'bird'): {show_count(1, 'bird')}")
    print(f"show_count(0, 'bird'): {show_count(0, 'bird')}")
    print(f"show_count(3, 'mouse', 'mice'): {show_count(3, 'mouse', 'mice')}")
    
    print(f"parse_token('12.5') -> {repr(parse_token('12.5'))}")
    print(f"parse_token('hello') -> {repr(parse_token('hello'))}")


if __name__ == "__main__":
    demo_duck_vs_nominal()
    demo_postels_law()
    demo_tuple_types()
    demo_unions()
