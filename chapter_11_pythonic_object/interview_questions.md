# Chapter 11 — Interview Questions: A Pythonic Object

---

## 🟢 L3

### Q1: What is the difference between `__repr__` and `__str__`?
`__repr__` is intended for developers. It should ideally return a string representing a valid Python expression that could recreate the object (e.g., `Point(1, 2)`). `__str__` is intended for end-users and should be readable. If `__str__` is not defined, Python falls back to `__repr__`.

---

### Q2: What is the difference between `@classmethod` and `@staticmethod`?
`@classmethod` changes a method to receive the class itself (`cls`) as the implicit first argument, rather than the instance (`self`). This makes it perfect for alternative constructors. `@staticmethod` receives no implicit first argument at all; it behaves exactly like a plain module-level function but lives inside the class namespace for organizational purposes.

---

## 🟡 L4

### Q3: How do you make a custom class hashable?
You must implement both `__eq__` and `__hash__`. Crucially, the fields used to compute the hash must be **immutable** for the lifetime of the object. If you change a value that affects the hash after the object is inserted into a dictionary or set, the object will effectively become lost in the hash table.

---

### Q4: Why would you use `__slots__`? What are the tradeoffs?
You use `__slots__ = ('attr1', 'attr2')` to tell CPython to store instance attributes in a fixed-size array instead of a dynamic dictionary (`__dict__`). This saves a massive amount of memory if you are creating millions of instances. 
The tradeoffs are: you cannot dynamically add new attributes at runtime, subclasses don't automatically inherit the memory savings (unless they also define `__slots__`), and instances cannot be the target of weak references unless `'__weakref__'` is explicitly included in the slots.

---

## 🔴 L5

### Q5: Explain Python's "name mangling" and why it exists.
If you prefix an attribute with two underscores (e.g., `__secret`), Python's compiler renames it to `_ClassName__secret`. Many developers mistakenly believe this is for "security" or strict privacy. It is actually designed to prevent **accidental namespace collisions** when someone subclasses your class and unknowingly creates an attribute with the same name, which would otherwise silently overwrite your internal state.

---

## 🟣 L6

### Q6: How does `__slots__` actually work under the hood at the C level?
When a class defines `__slots__`, CPython skips allocating a `__dict__` pointer on the instance C struct. Instead, it creates **descriptors** at the class level for every string defined in the `__slots__` tuple. 
When you access `obj.x`, Python looks at the class, finds the descriptor for `x`, and the descriptor calculates a fixed offset into the C struct of the instance to read or write the value directly from memory. It replaces expensive hash-table lookups with direct memory offset arithmetic.
