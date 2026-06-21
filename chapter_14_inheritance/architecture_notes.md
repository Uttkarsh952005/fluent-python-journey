# Chapter 14 — Architecture Notes: `super()` and C3 Linearization

---

## 1. How `super()` Actually Works at the C Level

When you call `super().method()` in Python 3, you are actually instantiating a dynamic proxy object. 

At compile-time, the bytecode compiler sees `super()` with no arguments and injects two invisible variables into the method's local scope:
*   `__class__`: The class where the method is currently defined.
*   `self`: The instance currently executing the method.

At runtime, the C implementation of `super` (`super_init` in `typeobject.c`) takes these two arguments and constructs a proxy object.
When you call `.method()` on this proxy, it:
1. Grabs the `__mro__` tuple from `type(self)`.
2. Finds the exact index of `__class__` in that MRO tuple.
3. Begins searching for `.method()` starting at index `+ 1`.

This guarantees that `super()` strictly delegates to the **next** class in the MRO, rather than arbitrarily searching up the tree.

---

## 2. The C3 Linearization Algorithm

Before Python 2.3, Python used a simple depth-first, left-to-right algorithm to build the MRO. This broke horribly in complex diamond inheritance (e.g., reaching `Root` via the left branch before the right branch had a chance to execute).

Python adopted the **C3 Linearization Algorithm** (first designed for Dylan in 1996). 

### How C3 Calculates the MRO
The MRO of a class `C` is the class `C` itself, followed by the **merge** of the MROs of its base classes, plus the list of base classes themselves.

`L(C(B1 ... BN)) = C + merge(L(B1) ... L(BN), B1 ... BN)`

The `merge` operation works by taking the first class in the lists that is **not** in the tail of any other list. 
If it finds a valid class, it adds it to the MRO and removes it from all lists. It repeats this until all lists are empty.
If at any point it cannot find a valid class (because the remaining classes conflict with each other's local precedence rules), it raises a `TypeError`, refusing to compile the class.

This strict algorithmic approach guarantees that:
1. `Root` is always called last.
2. Every class in a complex hierarchy is called exactly once.
3. Left-to-right declaration order is preserved absolutely.
