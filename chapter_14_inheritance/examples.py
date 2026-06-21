"""
Chapter 14: Inheritance: For Better or For Worse
================================================
Original implementations exploring the dangers of subclassing built-in
types (the C-trap), Method Resolution Order (MRO), and cooperative super().

Key concepts covered:
- The Built-in Subclassing Trap (dict vs UserDict)
- Cooperative Multiple Inheritance
- The Diamond Problem and __mro__
- Mixin Classes
"""

import sys
from collections import UserDict

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Part 1: The Built-in Subclassing Trap
# ─────────────────────────────────────────────────────────────────────────────
# CPython's native C implementation of `dict` often bypasses Python-level
# method overrides for performance.

class DoppelDict(dict):
    """Subclassing dict directly: A recipe for silent bugs."""
    def __setitem__(self, key, value):
        # We want to intercept all writes and append a warning
        super().__setitem__(key, [value] * 2)

class SafeDict(UserDict):
    """Subclassing UserDict: Safe and compliant."""
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)


def demo_built_in_trap() -> None:
    section("Part 1: The Built-in Subclassing Trap")
    
    # Direct assignment works for both
    dd = DoppelDict(one=1)
    dd['two'] = 2
    
    sd = SafeDict(one=1)
    sd['two'] = 2
    
    # BUT! Look what happens when internal C methods update the dict!
    dd.update(three=3)
    sd.update(three=3)
    
    print(f"Subclassing `dict`:      {dd}")
    print(f"Subclassing `UserDict`:  {sd}")
    print("\nNotice how `DoppelDict.update()` completely ignored our __setitem__!")
    print("The C implementation of dict.update bypasses Python overrides.")


# ─────────────────────────────────────────────────────────────────────────────
# Part 2: Cooperative Multiple Inheritance & MRO
# ─────────────────────────────────────────────────────────────────────────────
# Python resolves the Diamond Problem using the C3 Linearization Algorithm.
# `super()` does NOT mean "parent class". It means "the next class in the MRO."

class Root:
    def ping(self):
        print(f"  {self.__class__.__name__}.ping() in Root")

class A(Root):
    def ping(self):
        print(f"  {self.__class__.__name__}.ping() in A -> delegating...")
        super().ping()

class B(Root):
    def ping(self):
        print(f"  {self.__class__.__name__}.ping() in B -> delegating...")
        super().ping()

class Leaf(A, B):
    def ping(self):
        print(f"  {self.__class__.__name__}.ping() in Leaf -> delegating...")
        super().ping()


def demo_mro() -> None:
    section("Part 2: Multiple Inheritance & The MRO")
    
    leaf = Leaf()
    print("MRO of Leaf:")
    for cls in Leaf.__mro__:
        print(f"  - {cls.__name__}")
        
    print("\nExecuting ping() across the diamond:")
    leaf.ping()
    
    print("\nNotice how `super().ping()` in Class A didn't call Root!")
    print("It called Class B! `super()` delegates to the NEXT class in the MRO.")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_built_in_trap()
    demo_mro()
