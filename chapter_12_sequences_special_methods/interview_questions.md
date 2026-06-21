# Chapter 12 — Interview Questions: Sequences and Dunders

---

## 🟢 L3

### Q1: What methods are required to make an object act like a sequence?
To make an object behave like a native Python sequence (allowing iteration, `len()`, and indexing), you do not need to subclass anything. You just need to implement `__len__` and `__getitem__`.

---

### Q2: What happens if you slice a native Python list?
Slicing a built-in sequence like a list, tuple, or string always returns a **new object of the same type**. It does not return a view or a reference to the original object (unlike `numpy` arrays or `memoryview`). 

---

## 🟡 L4

### Q3: How do you handle slicing in a custom sequence class?
When a user writes `my_obj[1:5]`, Python passes a `slice(1, 5, None)` object to the `__getitem__(self, index)` method. You must check `isinstance(index, slice)` and explicitly write logic to handle it. Ideally, you should pass the sliced data into your class constructor so it returns a new instance of your custom class.

---

### Q4: When is `__getattr__` called?
`__getattr__` is only called as a fallback. It fires if, and only if, an attribute cannot be found in the instance `__dict__` or anywhere in its class hierarchy. If the attribute actually exists, `__getattr__` is bypassed entirely. (Contrast this with `__getattribute__`, which fires for *every* access).

---

## 🔴 L5

### Q5: How do you prevent attribute shadowing when using `__getattr__`?
If you use `__getattr__` to map `obj.x` to an internal data structure, a user could do `obj.x = 10`. This puts `'x': 10` in the instance `__dict__`. Because `__getattr__` is a fallback, subsequent lookups for `obj.x` will find the 10 and skip your dynamic logic. 
To prevent this, you must implement `__setattr__` and raise an `AttributeError` if the user tries to assign a value to a dynamically routed property like `x`.

---

## 🟣 L6

### Q6: How would you efficiently compute the equality of two very large sequences?
If you have two sequences with millions of elements, doing `tuple(seq1) == tuple(seq2)` is highly inefficient because it allocates two massive tuples in memory and iterates over both entirely.
Instead, you should first check if their lengths match. If they do, use `all(a == b for a, b in zip(seq1, seq2))`. This is highly memory efficient (using generators) and immediately short-circuits (stops evaluating) the moment it finds a single mismatch.
