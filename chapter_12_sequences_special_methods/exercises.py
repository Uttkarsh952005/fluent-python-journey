"""
Chapter 12: Exercises — Sequences and Attributes
================================================
Original exercises exploring custom sequence protocols and 
the dangers of dynamic attributes.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: Reversing a Sequence Natively
# ─────────────────────────────────────────────────────────────────────────────
# A sequence should support `reversed()`. If you don't implement `__reversed__`,
# Python falls back to using `__len__` and `__getitem__` backwards.
# Prove this works on a custom custom structure.

class Alphabet:
    def __init__(self):
        self.letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
    def __len__(self) -> int:
        return len(self.letters)
        
    def __getitem__(self, idx):
        return self.letters[idx]

def test_ex1_reversed() -> None:
    section("Exercise 1: Duck-typed Sequences")
    alpha = Alphabet()
    
    # We didn't define __reversed__, but this works anyway!
    rev = "".join(reversed(alpha))
    print(f"Reversed: {rev}")
    
    assert rev == "ZYXWVUTSRQPONMLKJIHGFEDCBA"
    assert rev[0] == "Z"
    print("✓ Exercise 1 passed")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: The __getattr__ Infinite Recursion Trap
# ─────────────────────────────────────────────────────────────────────────────
# If __getattr__ raises a standard Exception instead of AttributeError, 
# or if it accidentally accesses an undefined attribute inside itself, 
# it causes infinite recursion. 

class BadObject:
    def __getattr__(self, name):
        # BUG: We are trying to access self.target, but if 'target' isn't 
        # defined in __dict__, Python calls __getattr__ again!
        return self.target + name

def test_ex2_recursion() -> None:
    section("Exercise 2: The Recursion Trap")
    obj = BadObject()
    
    try:
        # Calling an undefined attribute triggers __getattr__
        val = obj.foo
        assert False, "Should have recurred infinitely"
    except RecursionError:
        print("Caught infinite RecursionError caused by __getattr__ looking up 'target'")
        print("✓ Exercise 2 passed")


if __name__ == "__main__":
    test_ex1_reversed()
    test_ex2_recursion()
