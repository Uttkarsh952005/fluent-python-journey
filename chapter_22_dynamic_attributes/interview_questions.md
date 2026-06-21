# Chapter 22 — Interview Questions: Dynamic Attributes

---

## 🟢 L3

### Q1: What is the main purpose of the `@property` decorator?
It allows you to define a method that is accessed exactly like an attribute. It enforces the "Uniform Access Principle", letting you seamlessly add validation logic (via a setter) or dynamic calculations (via a getter) to a class attribute without breaking backwards compatibility for code that was already using `obj.attribute`.

---

## 🟡 L4

### Q2: What is the difference between `__init__` and `__new__`?
`__new__` is the actual constructor. It is called before `__init__`, allocates memory, and physically returns the object. It is a static method that takes the class `cls` as its first argument. 
`__init__` is merely the initializer. It takes the object returned by `__new__` (passed as `self`) and attaches data to it. Most developers never need to override `__new__` unless they are building immutable types (like Tuples) or dynamic factories that might return an instance of a *different* class entirely.

---

## 🔴 L5

### Q3: What is the architectural difference between `__getattr__` and `__getattribute__`?
`__getattribute__` intercepts **every single attribute lookup**, regardless of whether the attribute exists or not. Overriding it is highly error-prone due to recursion risks.
`__getattr__` acts strictly as a **fallback**. It is only called by Python if the attribute cannot be found in the instance dictionary or the class tree. This makes it much safer and more useful for building dynamic wrappers (like converting dictionary keys into attributes).

---

## 🟣 L6

### Q4: How does `@functools.cached_property` achieve O(1) performance on subsequent lookups?
It hacks the standard CPython attribute lookup order. 
When you access `obj.data` for the first time, it executes the expensive function. Then, it physically writes the result directly into the instance's dictionary (`self.__dict__['data'] = result`).
Because Python checks the instance dictionary *before* it checks class-level descriptors (non-data descriptors), the second time you access `obj.data`, Python finds it in the `__dict__` and returns it instantly in O(1) time, completely bypassing the property method!
