# Chapter 16 — Interview Questions: Operator Overloading

---

## 🟢 L3

### Q1: What happens if `a + b` fails? How does Python recover?
When Python evaluates `a + b`, it calls `a.__add__(b)`. If `a` doesn't implement `__add__`, or if the method returns `NotImplemented`, Python does not immediately crash. It falls back to calling `b.__radd__(a)`. If that also returns `NotImplemented` or doesn't exist, Python finally raises a `TypeError`.

---

### Q2: What is the fundamental difference between `__add__` and `__iadd__`?
`__add__` maps to the `+` operator. It must **never** mutate the operands and must return a brand new object.
`__iadd__` maps to the `+=` operator (in-place addition). It **should** mutate the left operand in place to save memory, and it **must** return `self`.

---

## 🟡 L4

### Q3: What happens if a class does not implement `__iadd__` but the user runs `a += b`?
Python gracefully falls back to using `__add__`. It evaluates `a.__add__(b)` to create a completely new object, and then rebinds the variable `a` to point to that new object (`a = a + b`). This is why `+=` works on immutable types like strings and tuples.

---

### Q4: Why should you return `NotImplemented` instead of raising `TypeError` inside `__add__`?
If you raise `TypeError`, you immediately crash the program and stop the operator dispatch process. If you return `NotImplemented`, you signal to Python's execution engine that the left operand doesn't know how to handle the operation, allowing Python to politely ask the right operand by calling its `__radd__` method.

---

## 🔴 L5

### Q5: In rich comparisons (like `__eq__`), why is duck typing preferred over `isinstance` checks?
If you hardcode `isinstance(other, Vector)` inside `Vector.__eq__`, you prevent your `Vector` from ever being compared to other iterable structures that might mathematically represent the same data (like a `tuple` or a `list`). By using duck typing (e.g., trying to `zip()` them together and catching the `TypeError`), you create a much more flexible and Pythonic API.

---

## 🟣 L6

### Q6: How does CPython implement augmented assignment fallback at the C level?
In CPython, operators are mapped to C-struct slots in the `PyNumberMethods` struct attached to the class type. 
For `+=`, CPython checks the `nb_inplace_add` slot. If it is `NULL` (meaning `__iadd__` is not implemented), CPython immediately delegates to the `nb_add` slot. The resulting pointer from `nb_add` is then reassigned to the original variable reference in the local namespace array (`STORE_FAST` bytecode).
