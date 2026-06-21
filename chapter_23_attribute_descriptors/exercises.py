"""
Chapter 23: Exercises — The Storage Trap and Shadowing
======================================================
Original exercises demonstrating the two most dangerous logic bugs
when implementing custom descriptors.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Shared Storage Trap
# ─────────────────────────────────────────────────────────────────────────────

class BadStorageDescriptor:
    def __init__(self):
        # BUG: The descriptor stores the data on ITSELF.
        # Because descriptors are Class Attributes, this means ALL instances
        # of the managed class will share this exact same memory slot!
        self.data = 0

    def __get__(self, instance, owner):
        return self.data
        
    def __set__(self, instance, value):
        self.data = value

class BadClass:
    score = BadStorageDescriptor()

def test_ex1_storage_trap() -> None:
    section("Exercise 1: The Shared Storage Trap")
    
    player1 = BadClass()
    player2 = BadClass()
    
    player1.score = 100
    player2.score = 50
    
    # We expect player1 to be 100. Let's see what happened.
    print(f"  Player 1 score: {player1.score}")
    print(f"  Player 2 score: {player2.score}")
    
    if player1.score == 50:
        print("✓ Exercise 1 passed: Proved that storing data on `self` inside a")
        print("  descriptor corrupts data across all managed instances!")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: The Non-Overriding Shadow Trap
# ─────────────────────────────────────────────────────────────────────────────
# If a descriptor implements __get__ but NOT __set__, it is Non-Overriding.
# Python allows you to assign a value to it, but it silently bypasses the
# descriptor entirely and shadows it with an instance variable!

class NonOverridingDescriptor:
    def __get__(self, instance, owner):
        return "Descriptor Data"

class ShadowClass:
    data = NonOverridingDescriptor()

def test_ex2_shadowing() -> None:
    section("Exercise 2: The Non-Overriding Shadow Trap")
    
    obj = ShadowClass()
    print(f"  Before assignment: {obj.data}")
    
    # Because there is no __set__, Python just shoves "Hacked" directly
    # into obj.__dict__["data"], permanently hiding the descriptor.
    obj.data = "Hacked!"
    print(f"  After assignment:  {obj.data}")
    
    assert obj.data == "Hacked!"
    print("✓ Exercise 2 passed: Proved that missing __set__ allows the descriptor")
    print("  to be silently overwritten and shadowed by instance attributes.")


if __name__ == "__main__":
    test_ex1_storage_trap()
    test_ex2_shadowing()
