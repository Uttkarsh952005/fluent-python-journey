"""
Chapter 11: Mini Project — A Production-Grade Color Object
==========================================================
A practical implementation of a Pythonic object. We build an immutable, 
hashable, and memory-optimized `Color` class used in UI frameworks.

Concepts demonstrated:
- __slots__ for memory efficiency
- @classmethod for alternative constructors (from_hex)
- Rich string formatting (RGB vs HEX)
- True immutability for safe hashing
"""

import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

class Color:
    # Use slots to save memory when generating thousands of pixels/colors
    __slots__ = ('_r', '_g', '_b')
    
    def __init__(self, r: int, g: int, b: int):
        # Enforce 0-255 range and immutability by storing in private-ish fields
        self._r = max(0, min(255, int(r)))
        self._g = max(0, min(255, int(g)))
        self._b = max(0, min(255, int(b)))

    # Read-only properties make the object immutable
    @property
    def r(self) -> int: return self._r
    @property
    def g(self) -> int: return self._g
    @property
    def b(self) -> int: return self._b

    def __iter__(self):
        return iter((self.r, self.g, self.b))

    def __repr__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b})"

    def __str__(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}".upper()

    def __format__(self, fmt_spec: str) -> str:
        if fmt_spec == 'rgb':
            return f"rgb({self.r}, {self.g}, {self.b})"
        elif fmt_spec == 'hex':
            return str(self)
        else:
            return format(str(self), fmt_spec)

    def __eq__(self, other) -> bool:
        if isinstance(other, Color):
            return tuple(self) == tuple(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(tuple(self))

    @classmethod
    def from_hex(cls, hex_str: str) -> 'Color':
        """Alternative constructor parsing a hex string."""
        hex_str = hex_str.lstrip('#')
        if not re.fullmatch(r'[0-9a-fA-F]{6}', hex_str):
            raise ValueError(f"Invalid hex color: {hex_str}")
        
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return cls(r, g, b)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Color API Demonstration")
    print("=" * 60)

    # Standard instantiation
    c1 = Color(255, 90, 90)
    print(f"Developer representation (repr): {c1!r}")
    print(f"User representation (str):       {c1}")
    
    # Alternative constructor
    c2 = Color.from_hex("#FF5A5A")
    print(f"From Hex representation:         {c2!r}")
    
    # Equality and Hashing
    print(f"c1 == c2? {c1 == c2}")
    
    palette = {c1, Color(0, 0, 0), Color(255, 255, 255)}
    print(f"Palette size: {len(palette)}")  # c1 and c2 are identical, set deduplicates
    
    # Custom formatting
    print(f"Formatted as RGB: {c1:rgb}")
    print(f"Formatted as HEX: {c1:hex}")

if __name__ == "__main__":
    main()
