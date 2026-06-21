"""
Chapter 16: Operator Overloading
================================
Original implementations exploring the mechanics of infix operators,
the reverse operator fallback (__radd__), and rich comparisons.

Key concepts covered:
- Infix operators (__add__)
- The Reverse Fallback (__radd__)
- The NotImplemented singleton
- Rich Comparisons (__eq__)
"""

import sys
import math
from array import array

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Infix Operators & The Reverse Fallback
# ─────────────────────────────────────────────────────────────────────────────

class Vector:
    def __init__(self, components):
        self._components = tuple(components)

    def __iter__(self):
        return iter(self._components)
        
    def __repr__(self):
        return f"Vector{self._components}"

    # --- Addition ---
    def __add__(self, other):
        """Called for: Vector + <something>"""
        try:
            # Try to build a new Vector by zipping and adding components
            pairs = zip(self, other, strict=False)
            return Vector(a + b for a, b in pairs)
        except TypeError:
            # We don't know how to add this type. Tell Python to try the 
            # reverse operator (__radd__) on the OTHER operand!
            return NotImplemented

    def __radd__(self, other):
        """Called for: <something> + Vector (if <something> returned NotImplemented)"""
        # Addition is commutative, so we can just delegate back to __add__
        return self + other

    # --- Multiplication (Scalar) ---
    def __mul__(self, scalar):
        try:
            factor = float(scalar)
        except ValueError:
            return NotImplemented
        return Vector(n * factor for n in self)
        
    def __rmul__(self, scalar):
        return self * scalar

    # --- Rich Comparisons ---
    def __eq__(self, other):
        if isinstance(other, Vector):
            return self._components == other._components
        # If we return NotImplemented, Python will evaluate other.__eq__(self)
        return NotImplemented


def demo_infix_operators() -> None:
    section("Part 1: Infix Operators and Reverse Fallbacks")
    
    v1 = Vector([1, 2, 3])
    v2 = Vector([10, 20, 30])
    
    # 1. Standard __add__
    print(f"Vector + Vector: {v1 + v2}")
    
    # 2. Duck Typing __add__ (Tuple is iterable, so zip() works!)
    print(f"Vector + Tuple:  {v1 + (100, 200, 300)}")
    
    # 3. The Reverse Fallback (__radd__)
    # Tuple.__add__(Vector) returns NotImplemented.
    # Python then successfully executes Vector.__radd__(Tuple).
    print(f"Tuple + Vector:  {(100, 200, 300) + v1}")
    
    # 4. Scalar multiplication
    print(f"Vector * 5:      {v1 * 5}")
    print(f"5 * Vector:      {5 * v1}")


def demo_comparisons() -> None:
    section("Part 2: Rich Comparisons")
    v1 = Vector([1, 2])
    v2 = Vector([1, 2])
    
    print(f"v1 == v2:        {v1 == v2}")
    print(f"v1 == [1, 2]:    {v1 == [1, 2]} (Returned NotImplemented, evaluated to False)")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_infix_operators()
    demo_comparisons()
