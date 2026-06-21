"""
Chapter 11: A Pythonic Object
=============================
Original implementations exploring object representations, formatting, 
immutability, hashing, and memory optimizations via __slots__.

Key concepts covered:
- Object representations: __str__, __repr__, __bytes__, __format__
- Alternative constructors with @classmethod
- Immutability and Hashing (__hash__, @property)
- Pattern matching support (__match_args__)
- Memory optimization (__slots__)
"""

import sys
import math
from array import array

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Part 1: A Complete Pythonic Object
# ─────────────────────────────────────────────────────────────────────────────

class Vector2d:
    """
    A 2-dimensional vector demonstrating the full suite of Pythonic
    dunder methods for object representation, formatting, and hashing.
    """
    
    # Class attribute used for binary serialization
    typecode = 'd'
    
    # Enables positional pattern matching (Python 3.10+)
    __match_args__ = ('x', 'y')

    def __init__(self, x: float, y: float):
        # We store them as private attributes since we want them to be read-only properties
        self.__x = float(x)
        self.__y = float(y)

    @property
    def x(self) -> float:
        return self.__x

    @property
    def y(self) -> float:
        return self.__y

    # Iteration makes unpacking work: x, y = my_vector
    def __iter__(self):
        return (i for i in (self.x, self.y))

    def __repr__(self) -> str:
        class_name = type(self).__name__
        return f"{class_name}({self.x!r}, {self.y!r})"

    def __str__(self) -> str:
        return str(tuple(self))

    def __bytes__(self) -> bytes:
        return (bytes([ord(self.typecode)]) +
                bytes(array(self.typecode, self)))

    def __eq__(self, other) -> bool:
        return tuple(self) == tuple(other)

    def __hash__(self) -> int:
        # Hashing requires immutability. We hash the components.
        return hash((self.x, self.y))

    def __abs__(self) -> float:
        return math.hypot(self.x, self.y)

    def __bool__(self) -> bool:
        return bool(abs(self))

    def angle(self) -> float:
        return math.atan2(self.y, self.x)

    def __format__(self, fmt_spec: str = '') -> str:
        if fmt_spec.endswith('p'):  # Custom 'p' specifier for polar coordinates
            fmt_spec = fmt_spec[:-1]
            coords = (abs(self), self.angle())
            outer_fmt = '<{}, {}>'
        else:
            coords = self
            outer_fmt = '({}, {})'
            
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(*components)

    @classmethod
    def frombytes(cls, octets: bytes) -> 'Vector2d':
        """Alternative constructor leveraging @classmethod."""
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(*memv)

def demo_vector2d() -> None:
    section("Part 1: The Pythonic Vector2d")
    v1 = Vector2d(3, 4)
    print(f"repr: {v1!r}")
    print(f"str:  {v1}")
    
    # Unpacking
    x, y = v1
    print(f"unpacking: x={x}, y={y}")
    
    # Hashing allows it to be used in sets
    v2 = Vector2d(3.1, 4.2)
    s = {v1, v2}
    print(f"In a set: {s}")
    
    # Formatting
    print(f"format default: {v1}")
    print(f"format float:   {v1:.2f}")
    print(f"format polar:   {v1:.3ep}")  # Using our custom 'p' specifier
    
    # Bytes and Alternative Constructor
    dumped = bytes(v1)
    print(f"bytes: {dumped}")
    v3 = Vector2d.frombytes(dumped)
    print(f"Restored from bytes: {v3!r}")
    assert v1 == v3


# ─────────────────────────────────────────────────────────────────────────────
# Part 2: Saving Memory with __slots__
# ─────────────────────────────────────────────────────────────────────────────

class SlotVector:
    """
    By default, Python stores instance attributes in a per-instance dict (__dict__).
    This is highly dynamic but costs significant memory.
    __slots__ tells Python to store attributes in a fixed-size array instead.
    """
    __slots__ = ('__x', '__y')
    
    def __init__(self, x: float, y: float):
        self.__x = float(x)
        self.__y = float(y)

def demo_slots() -> None:
    section("Part 2: __slots__ Memory Optimization")
    v_dict = Vector2d(1, 2)
    v_slot = SlotVector(1, 2)
    
    print(f"Normal vector has __dict__: {hasattr(v_dict, '__dict__')}")
    print(f"Slot vector has __dict__:   {hasattr(v_slot, '__dict__')}")
    
    try:
        v_slot.z = 3  # Attempting to dynamically add an attribute
    except AttributeError as e:
        print(f"Adding attribute to slot object fails: {e}")

if __name__ == "__main__":
    demo_vector2d()
    demo_slots()
