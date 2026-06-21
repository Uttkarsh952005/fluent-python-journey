"""
Chapter 16: Mini Project — A 3D Matrix Math Module
==================================================
A practical demonstration of robust operator overloading. We implement
a 3x3 Matrix capable of scalar multiplication, matrix addition, matrix
dot products (@), and fast in-place mutation (+=).
"""

import sys
from array import array

sys.stdout.reconfigure(encoding="utf-8")

class Matrix3D:
    """A 3x3 mathematical matrix."""
    def __init__(self, data):
        data_list = list(data)
        if len(data_list) != 9:
            raise ValueError("Matrix3D requires exactly 9 elements")
        self._data = array('d', data_list)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        d = self._data
        return (f"Matrix3D([\n"
                f"  {d[0]:.1f}, {d[1]:.1f}, {d[2]:.1f},\n"
                f"  {d[3]:.1f}, {d[4]:.1f}, {d[5]:.1f},\n"
                f"  {d[6]:.1f}, {d[7]:.1f}, {d[8]:.1f}\n])")

    # ── Infix Addition ────────────────────────────────────────────────────────
    
    def __add__(self, other):
        """Matrix + Matrix -> New Matrix"""
        if isinstance(other, Matrix3D):
            # Safe zip because we validated length 9 on creation
            return Matrix3D(a + b for a, b in zip(self, other))
        return NotImplemented

    # ── Scalar Multiplication ─────────────────────────────────────────────────
    
    def __mul__(self, scalar):
        """Matrix * Scalar -> New Matrix"""
        try:
            factor = float(scalar)
        except ValueError:
            return NotImplemented
        return Matrix3D(val * factor for val in self)

    def __rmul__(self, scalar):
        """Scalar * Matrix -> New Matrix"""
        return self * scalar

    # ── In-Place Addition ─────────────────────────────────────────────────────
    
    def __iadd__(self, other):
        """Matrix += Matrix -> Mutates self"""
        if isinstance(other, Matrix3D):
            for i, val in enumerate(other):
                self._data[i] += val
            return self  # CRITICAL: Must return self
        return NotImplemented


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Matrix3D Operator Pipeline")
    print("=" * 60)

    m1 = Matrix3D([1, 0, 0, 0, 1, 0, 0, 0, 1])  # Identity
    m2 = Matrix3D([2, 2, 2, 3, 3, 3, 4, 4, 4])
    
    print("\n1. Scalar Multiplication (m1 * 5):")
    print(m1 * 5)
    
    print("\n2. Matrix Addition (m1 + m2):")
    print(m1 + m2)
    
    print("\n3. In-Place Addition (m2 += m1):")
    m2_id = id(m2)
    m2 += m1
    print(f"ID before: {m2_id} | ID after: {id(m2)} (Matched: {m2_id == id(m2)})")
    print(m2)
    
    print("\n4. Handling unsupported types (m1 + 5):")
    try:
        m1 + 5
    except TypeError as e:
        print(f"Caught fallback failure: {e}")

if __name__ == "__main__":
    main()
