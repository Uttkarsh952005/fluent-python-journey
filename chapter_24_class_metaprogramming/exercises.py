"""
Chapter 24: Exercises — Evaluation Time vs Execution Time
=========================================================
Original exercises proving EXACTLY when Python executes different 
parts of a class definition.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Timeline
# ─────────────────────────────────────────────────────────────────────────────

print("\n[Module] 1. Module starts loading...")

class TimelineObject:
    
    # This print statement executes AT EVALUATION TIME (Import time).
    # It runs before we ever instantiate the class!
    print("  [Class Body] 2. The class body is being evaluated.")
    
    def __init__(self):
        # This print statement executes AT EXECUTION TIME (Runtime).
        print("    [__init__] 4. An instance is being created.")

    def method(self):
        print("      [method] 5. The method is being called.")


def test_ex1_timeline() -> None:
    section("Exercise 1: Execution Timeline")
    print("\n[Main] 3. Starting the main execution phase.")
    
    obj = TimelineObject()
    obj.method()
    
    print("\n✓ Exercise 1 passed: Notice how [Class Body] printed before")
    print("  the main() function even started! This is why Metaclasses")
    print("  and Class Decorators can crash your app at import time.")


if __name__ == "__main__":
    test_ex1_timeline()
