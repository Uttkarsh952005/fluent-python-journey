"""
Chapter 16: Exercises — In-Place Operators and The None Trap
============================================================
Original exercises demonstrating the rules of __iadd__ (+=) and
the fatal mistake of forgetting to return `self`.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Missing Return in __iadd__
# ─────────────────────────────────────────────────────────────────────────────
# If a class implements __iadd__, Python translates `a += b` to `a = a.__iadd__(b)`.
# This means __iadd__ MUST return `self`. If it returns nothing, it returns None,
# and `a` gets permanently overwritten with `None`!

class BrokenWallet:
    def __init__(self, amount):
        self.amount = amount
        
    def __iadd__(self, other):
        # BUG: It mutates self, but forgets to return self!
        self.amount += other

class WorkingWallet:
    def __init__(self, amount):
        self.amount = amount
        
    def __iadd__(self, other):
        self.amount += other
        # MUST return self!
        return self


def test_ex1_inplace() -> None:
    section("Exercise 1: The In-Place Return Trap")
    
    bw = BrokenWallet(100)
    print(f"BrokenWallet initial type: {type(bw).__name__}")
    bw += 50
    print(f"BrokenWallet type after += 50: {type(bw).__name__}")
    assert bw is None, "The object should have been overwritten with None!"
    
    ww = WorkingWallet(100)
    ww += 50
    print(f"WorkingWallet amount after += 50: {ww.amount}")
    assert ww.amount == 150
    assert isinstance(ww, WorkingWallet)
    print("✓ Exercise 1 passed: Proved that __iadd__ must return self.")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Fallback of += without __iadd__
# ─────────────────────────────────────────────────────────────────────────────
# If a class does NOT implement __iadd__, Python gracefully falls back to 
# `a = a.__add__(b)`. This means `a` is bound to a completely new object!

class ImmutableScore:
    def __init__(self, val):
        self.val = val
        
    def __add__(self, other):
        # Returns a NEW object
        return ImmutableScore(self.val + other)

def test_ex2_fallback() -> None:
    section("Exercise 2: Fallback of += to __add__")
    
    s = ImmutableScore(10)
    original_id = id(s)
    
    s += 5
    new_id = id(s)
    
    print(f"Value: {s.val}")
    print(f"IDs match? {original_id == new_id} (It's a completely new object!)")
    
    assert original_id != new_id
    assert s.val == 15
    print("✓ Exercise 2 passed: Proved that += falls back to __add__ and creates new objects.")


if __name__ == "__main__":
    test_ex1_inplace()
    test_ex2_fallback()
