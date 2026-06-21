# Chapter 11 — Architecture Notes: `__slots__` and Descriptors

---

## 1. The Heavy Cost of `__dict__`

In standard Python, every class instance is essentially a wrapper around a hash table (the `__dict__`). 

When you write:
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```
CPython allocates the instance struct, and then allocates a separate, dynamic dictionary object to hold `'x'` and `'y'`. Dictionaries have significant memory overhead because they over-allocate buckets to maintain fast O(1) lookups and handle dynamic resizing. If you create 1,000,000 `Point` objects, you are creating 1,000,000 dictionaries.

---

## 2. How `__slots__` Works at the Bytecode/C Level

When you define `__slots__ = ('x', 'y')`, CPython alters the memory layout of the instances.

1. **No Dict Pointer:** The C struct for the instance (`PyObject`) no longer has a pointer allocated for a `__dict__`.
2. **Fixed Struct:** The instance struct is allocated with exactly enough space for an array of pointers (one for `x`, one for `y`).
3. **Class-Level Descriptors:** The binding happens on the *class*. CPython automatically generates `member_descriptor` objects and attaches them to the class dictionary for each slot.

```python
class SlotPoint:
    __slots__ = ('x', 'y')

print(type(SlotPoint.x))  # <class 'member_descriptor'>
```

---

## 3. The Access Mechanism (Offset Arithmetic)

When you execute `p.x` on a slotted object:
1. Python checks the instance `__dict__` (it doesn't exist).
2. It falls back to the class `SlotPoint` and finds the `member_descriptor` for `x`.
3. The descriptor holds a **memory offset integer**. 
4. The descriptor executes C code that basically says: "Take the memory address of the instance `p`, add the offset for `x`, and return the PyObject pointer located there."

### Architectural Conclusion
`__slots__` replaces dynamic hash-table lookups with hardcoded C-struct memory offset arithmetic. This is why it reduces memory overhead (no dicts) and slightly improves attribute access speed, but limits dynamic flexibility.
