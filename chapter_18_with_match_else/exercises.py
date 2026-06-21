"""
Chapter 18: Exercises — Exception Swallowing and Missing Finally
================================================================
Original exercises demonstrating the two most dangerous pitfalls 
when building custom context managers.
"""

import sys
from contextlib import contextmanager

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Exception Swallower
# ─────────────────────────────────────────────────────────────────────────────
# If __exit__ returns True, Python assumes the exception was handled and
# silently drops it. This can hide fatal errors.

class DangerousSwallower:
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, traceback):
        print(f"  [Swallower] Caught {exc_type.__name__}: {exc_val}")
        # BUG: Returning True silences the crash!
        return True

def test_ex1_swallower() -> None:
    section("Exercise 1: The Exception Swallower")
    
    print("  Entering dangerous block...")
    with DangerousSwallower():
        # This exception will completely vanish
        raise RuntimeError("FATAL DATABASE CORRUPTION")
        
    print("  Exited block safely! (But wait, we shouldn't have!)")
    print("✓ Exercise 1 passed: Proved that returning True from __exit__ drops exceptions.")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: The Missing Finally in @contextmanager
# ─────────────────────────────────────────────────────────────────────────────
# When an exception occurs inside a `with` block using @contextmanager,
# the exception is injected back into the generator exactly at the `yield`.
# If there is no `finally` block, the generator crashes, and teardown is skipped!

@contextmanager
def broken_db_connection():
    print("  [DB] Connecting...")
    yield "Connection Object"
    # BUG: If an exception happens inside the 'with' block, the generator
    # crashes at the `yield` line. This teardown line will NEVER run!
    print("  [DB] Disconnecting safely (This will not print!)...")

def test_ex2_missing_finally() -> None:
    section("Exercise 2: The Missing Finally Trap")
    
    try:
        with broken_db_connection() as conn:
            print("  [DB] Running query...")
            raise ValueError("Query syntax error!")
    except ValueError:
        print("  [Main] Caught the ValueError.")
        
    print("✓ Exercise 2 passed: Notice that 'Disconnecting safely' was never printed!")
    print("  Always wrap the yield in a try/finally block!")


if __name__ == "__main__":
    test_ex1_swallower()
    test_ex2_missing_finally()
