"""
Chapter 12: Special Methods for Sequences
=========================================
Original implementations exploring multidimensional sequences, 
slicing mechanics, dynamic attribute access, and hashing using reduce.

Key concepts covered:
- Sequence protocol (__len__, __getitem__)
- Slicing awareness in __getitem__
- Dynamic attribute routing (__getattr__, __setattr__)
- Efficient hashing of N-dimensional structures (functools.reduce)
"""

import sys
import math
import reprlib
import operator
import functools
from array import array

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Part 1: The N-Dimensional Vector
# ─────────────────────────────────────────────────────────────────────────────

class Vector:
    """
    An N-dimensional vector that behaves like a native Python sequence.
    """
    typecode = 'd'
    shortcut_names = 'xyzt'

    def __init__(self, components):
        # Store components as a flat, contiguous memory array
        self._components = array(self.typecode, components)

    # ── Sequence Protocol ───────────────────────────────────────────────────
    
    def __len__(self) -> int:
        return len(self._components)

    def __getitem__(self, index):
        cls = type(self)
        if isinstance(index, slice):
            # If sliced, return a NEW Vector instance, not just an array
            return cls(self._components[index])
        elif isinstance(index, int):
            return self._components[index]
        else:
            msg = f'{cls.__name__} indices must be integers or slices, not {type(index).__name__}'
            raise TypeError(msg)

    # ── Dynamic Attributes ──────────────────────────────────────────────────
    
    def __getattr__(self, name: str):
        cls = type(self)
        if len(name) == 1:
            pos = cls.shortcut_names.find(name)
            if 0 <= pos < len(self._components):
                return self._components[pos]
        msg = f'{cls.__name__!r} object has no attribute {name!r}'
        raise AttributeError(msg)

    def __setattr__(self, name: str, value):
        cls = type(self)
        # Prevent shadowing of 'x', 'y', 'z', 't' or other single-letter names
        if len(name) == 1:
            if name in cls.shortcut_names:
                error = f'readonly attribute {name!r}'
            elif name.islower():
                error = f"can't set attributes 'a' to 'z' in {cls.__name__!r}"
            else:
                error = ''
            if error:
                raise AttributeError(error)
        # Fall back to standard assignment for everything else (like _components)
        super().__setattr__(name, value)

    # ── Comparison and Hashing ──────────────────────────────────────────────
    
    def __eq__(self, other) -> bool:
        # Fast path for length mismatch, zip() stops at the shortest iterable
        if isinstance(other, Vector):
            return (len(self) == len(other) and 
                    all(a == b for a, b in zip(self, other)))
        return NotImplemented

    def __hash__(self) -> int:
        # Map hash() to all components, then XOR them together using reduce
        hashes = map(hash, self._components)
        return functools.reduce(operator.xor, hashes, 0)

    # ── Representation ──────────────────────────────────────────────────────
    
    def __repr__(self) -> str:
        # reprlib limits the output length for massive vectors (e.g. 1000 items)
        components = reprlib.repr(self._components)
        components = components[components.find('['):-1]
        return f'Vector({components})'
        
    def __str__(self) -> str:
        return str(tuple(self))


def demo_vector() -> None:
    section("Part 1: Slicing and Sequence Protocol")
    v = Vector(range(7))
    print(f"Vector: {v!r}")
    print(f"Length: {len(v)}")
    print(f"v[1:4]: {v[1:4]!r} (Notice it returns a Vector, not an array!)")
    print(f"v[-1]:  {v[-1]}")
    
    section("Part 2: Dynamic Attributes")
    v2 = Vector([10.0, 20.0, 30.0])
    print(f"v2.x: {v2.x}, v2.y: {v2.y}, v2.z: {v2.z}")
    
    try:
        v2.x = 99
    except AttributeError as e:
        print(f"Prevented shadowing (setattr override): {e}")

    section("Part 3: Hashing and Equality")
    v3 = Vector([10.0, 20.0, 30.0])
    print(f"v2 == v3: {v2 == v3}")
    
    grid = {v2: "Position A"}
    print(f"Hash lookup works! v3 retrieves: {grid[v3]}")


if __name__ == "__main__":
    demo_vector()
