"""
Chapter 18: with, match, and else Blocks
========================================
Original implementations exploring Context Managers (both class-based 
and generator-based) and the unusual behavior of 'else' blocks on loops.

Key concepts covered:
- Class-based Context Managers (__enter__ / __exit__)
- Generator-based Context Managers (@contextmanager)
- for/else and try/else patterns
"""

import sys
import time
from contextlib import contextmanager

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Class-Based Context Manager
# ─────────────────────────────────────────────────────────────────────────────
# A context manager guarantees that teardown code runs, even if an 
# exception is raised inside the 'with' block.

class Timer:
    """A context manager that measures execution time."""
    def __enter__(self):
        self.start = time.perf_counter()
        # The value returned here is bound to the `as` variable
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start
        print(f"  [Timer] Block took {self.elapsed:.4f}s")
        # Returning None (or False) means: propagate any exceptions.
        # Returning True means: swallow the exception silently.
        return None

def demo_class_context() -> None:
    section("Part 1: Class-Based Context Manager")
    with Timer() as t:
        print("  Executing heavy workload...")
        time.sleep(0.1)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Generator-Based Context Manager (@contextmanager)
# ─────────────────────────────────────────────────────────────────────────────
# Instead of writing a full class, we can use a generator. 
# Everything before `yield` is __enter__. Everything after is __exit__.

@contextmanager
def temporary_uppercase(text_list):
    """Temporarily uppercases a list of strings, then restores them."""
    original = list(text_list)
    try:
        for i in range(len(text_list)):
            text_list[i] = text_list[i].upper()
        # Execution yields control to the `with` block body
        yield text_list
    finally:
        # This acts as the __exit__. The `finally` is critical!
        for i in range(len(original)):
            text_list[i] = original[i]

def demo_generator_context() -> None:
    section("Part 2: @contextmanager")
    names = ['alice', 'bob']
    print(f"  Before: {names}")
    
    with temporary_uppercase(names) as upper_names:
        print(f"  Inside with: {upper_names}")
        
    print(f"  After:  {names}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. The 'else' Block on Loops (for/else)
# ─────────────────────────────────────────────────────────────────────────────
# `else` on a `for` loop ONLY executes if the loop completed naturally 
# (i.e., it was NOT aborted by a `break` statement).

def find_target(items, target):
    for item in items:
        if item == target:
            print(f"  Found {target}! Aborting search.")
            break
    else:
        # Executes only if the break was never hit
        print(f"  {target} was not found. Reached end of loop.")

def demo_for_else() -> None:
    section("Part 3: for / else behavior")
    data = [1, 2, 3, 4]
    find_target(data, 3)
    find_target(data, 99)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_class_context()
    demo_generator_context()
    demo_for_else()
