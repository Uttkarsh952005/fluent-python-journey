"""
Chapter 9: Exercises — Decorators and Closures
==============================================
Original exercises applying closures and decorators to solve practical problems.
"""

import sys
import functools

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Accumulator Closure
# ─────────────────────────────────────────────────────────────────────────────
# Write a function `make_accumulator` that returns a closure.
# The closure should accept a number and return the total sum of all numbers 
# passed to it so far. Use `nonlocal`.

def make_accumulator():
    # TODO: Initialize total
    total = 0
    def accumulator(value: int | float) -> int | float:
        # TODO: Implement accumulation using nonlocal
        nonlocal total
        total += value
        return total
    return accumulator

def test_ex1_accumulator() -> None:
    section("Exercise 1: Accumulator Closure")
    acc = make_accumulator()
    assert acc(5) == 5
    assert acc(10) == 15
    assert acc(-2) == 13
    print("✓ Exercise 1 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: A Retry Decorator
# ─────────────────────────────────────────────────────────────────────────────
# Write a `@retry` decorator that catches any Exception raised by the decorated 
# function and retries it up to `max_attempts` times. If it still fails, raise
# the final exception. Use `functools.wraps`.

def retry(max_attempts: int = 3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # TODO: Implement retry logic
            last_err = None
            for _ in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_err = e
            if last_err is not None:
                raise last_err
        return wrapper
    return decorator

def test_ex2_retry() -> None:
    section("Exercise 2: Retry Decorator")
    
    fails = 0
    
    @retry(max_attempts=3)
    def flacky_service():
        nonlocal fails
        fails += 1
        if fails < 3:
            raise ValueError("Service unavailable")
        return "Success!"
        
    result = flacky_service()
    print(f"flacky_service returned: {result} after {fails} attempts")
    assert result == "Success!" and fails == 3, "Exercise 2 failed"
    print("✓ Exercise 2 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 3: Access Control with Decorators
# ─────────────────────────────────────────────────────────────────────────────
# Create a `@requires_admin` decorator that checks a global `CURRENT_USER` dict.
# If `CURRENT_USER.get('role')` is not 'admin', raise a PermissionError.
# Otherwise, execute the function.

CURRENT_USER = {"name": "guest", "role": "guest"}

def requires_admin(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # TODO: Implement permission check
        if CURRENT_USER.get("role") != "admin":
            raise PermissionError("Admin privileges required")
        return func(*args, **kwargs)
    return wrapper

@requires_admin
def delete_database():
    return "DB Deleted"

def test_ex3_access_control() -> None:
    section("Exercise 3: Access Control Decorator")
    
    global CURRENT_USER
    
    # Try as guest
    try:
        delete_database()
        assert False, "Should have raised PermissionError"
    except PermissionError:
        print("Blocked guest successfully.")
        
    # Elevate to admin
    CURRENT_USER["role"] = "admin"
    res = delete_database()
    print(f"Admin action: {res}")
    assert res == "DB Deleted", "Exercise 3 failed"
    print("✓ Exercise 3 passed")


if __name__ == "__main__":
    test_ex1_accumulator()
    test_ex2_retry()
    test_ex3_access_control()
