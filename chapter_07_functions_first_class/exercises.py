"""
Chapter 7: Exercises — Functions as First-Class Objects
=========================================================
Original exercises exploring functional features, callables, and parameter signatures.
"""

import sys
import collections
from operator import attrgetter, methodcaller
from functools import partial
from typing import Callable, Iterable, Any

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: Custom Higher-Order Function
# ─────────────────────────────────────────────────────────────────────────────
# Implement `filter_map`, a function that takes two functions (`mapper` and `predicate`)
# and an iterable. It should return a list of mapped values for items that pass the predicate.
# Do this without using the built-in map/filter.

def filter_map(mapper: Callable, predicate: Callable, iterable: Iterable) -> list:
    """Apply mapper to items in iterable that pass predicate."""
    # TODO: Implement using a list comprehension
    return [mapper(x) for x in iterable if predicate(x)]

def test_ex1_filter_map() -> None:
    section("Exercise 1: filter_map")
    nums = [1, 2, 3, 4, 5, 6]
    # Keep evens, square them
    res = filter_map(lambda x: x**2, lambda x: x % 2 == 0, nums)
    print(f"filter_map result: {res}")
    assert res == [4, 16, 36], "Exercise 1 failed"
    print("✓ Exercise 1 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Fredrik Lundh's Lambda Refactoring
# ─────────────────────────────────────────────────────────────────────────────
# Below is a hard-to-read lambda used to parse a specific log line format:
# "[INFO] 2023-10-01 User logged in" -> ('INFO', 'User logged in')
# Refactor it into a proper `def` function for better readability.

# BAD:
parse_log_bad = lambda line: (line.split(']')[0][1:], line.split(' ', 2)[2])

# GOOD:
def parse_log(line: str) -> tuple[str, str]:
    """Parse a log line into (level, message)."""
    # TODO: Implement a readable version of the lambda above
    parts = line.split(' ', 2)
    level = parts[0].strip('[]')
    message = parts[2]
    return level, message

def test_ex2_lambda_refactoring() -> None:
    section("Exercise 2: Lambda Refactoring")
    log = "[INFO] 2023-10-01 User logged in"
    expected = ('INFO', 'User logged in')
    
    assert parse_log_bad(log) == expected, "Bad lambda broken"
    res = parse_log(log)
    print(f"Parsed: {res}")
    assert res == expected, "Exercise 2 failed"
    print("✓ Exercise 2 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 3: The Stateful Accumulator (__call__)
# ─────────────────────────────────────────────────────────────────────────────
# Create a class `Accumulator` that acts as a function.
# When called with a number, it adds it to a running total and returns the new total.
# When called with no arguments, it returns the current total without adding anything.

class Accumulator:
    def __init__(self, initial: int = 0):
        # TODO: Initialize state
        self.total = initial
        
    def __call__(self, value: int | None = None) -> int:
        # TODO: Implement logic
        if value is not None:
            self.total += value
        return self.total

def test_ex3_accumulator() -> None:
    section("Exercise 3: Stateful Accumulator")
    acc = Accumulator(10)
    
    assert callable(acc), "Accumulator is not callable!"
    
    v1 = acc(5)
    v2 = acc(20)
    v3 = acc()
    
    print(f"Accumulator results: {v1}, {v2}, {v3}")
    assert v1 == 15 and v2 == 35 and v3 == 35, "Exercise 3 failed"
    print("✓ Exercise 3 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 4: Positional-Only and Keyword-Only Signatures
# ─────────────────────────────────────────────────────────────────────────────
# Implement a function `create_user` that takes:
# 1. `username` as positional-only
# 2. `email` as positional or keyword
# 3. `role` and `active` as keyword-only (active defaults to True)
# Return a dictionary of these values.

# TODO: Define create_user with the exact signature required.
def create_user(username, /, email, *, role, active=True):
    return {
        "username": username,
        "email": email,
        "role": role,
        "active": active
    }

def test_ex4_signatures() -> None:
    section("Exercise 4: Advanced Signatures")
    
    # Valid call
    u = create_user("alice", "alice@example.com", role="admin")
    print(f"Created user: {u}")
    assert u == {"username": "alice", "email": "alice@example.com", "role": "admin", "active": True}
    
    # Verify positional-only
    try:
        create_user(username="bob", email="bob@a.com", role="user")
        assert False, "Should have raised TypeError (positional-only)"
    except TypeError:
        pass
        
    # Verify keyword-only
    try:
        create_user("bob", "bob@a.com", "user")
        assert False, "Should have raised TypeError (keyword-only)"
    except TypeError:
        pass
        
    print("✓ Exercise 4 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 5: Cleaning up map() with operator & partial
# ─────────────────────────────────────────────────────────────────────────────
# Given a list of user objects, extract their names, uppercase them, and prefix with "USER: ".
# Do this by composing `map` with `operator` and `functools.partial` instead of using a lambda.

User = collections.namedtuple('User', 'name age')
users = [User('alice', 30), User('bob', 25), User('charlie', 35)]

# TODO: Define `get_name` using operator.attrgetter
get_name = attrgetter('name')

# TODO: Define `uppercase` using operator.methodcaller
uppercase = methodcaller('upper')

# TODO: Define `prefix` using functools.partial and str.__add__ 
# (Wait, str.__add__ takes self and other. partial(str.__add__, "USER: ") won't work well 
# because it prepends to "USER: ". Alternatively, a simpler function is fine if needed, 
# but let's see: str.__add__("USER: ", "ALICE") works!)
prefix = partial(str.__add__, "USER: ")

def process_user(u: User) -> str:
    # A mini pipeline without lambdas
    return prefix(uppercase(get_name(u)))

def test_ex5_functional_primitives() -> None:
    section("Exercise 5: functional primitives")
    
    # Apply pipeline
    result = list(map(process_user, users))
    print(f"Processed users: {result}")
    
    expected = ["USER: ALICE", "USER: BOB", "USER: CHARLIE"]
    assert result == expected, "Exercise 5 failed"
    print("✓ Exercise 5 passed")


if __name__ == "__main__":
    test_ex1_filter_map()
    test_ex2_lambda_refactoring()
    test_ex3_accumulator()
    test_ex4_signatures()
    test_ex5_functional_primitives()
