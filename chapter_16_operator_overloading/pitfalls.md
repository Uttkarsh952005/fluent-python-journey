# Chapter 16 — Pitfalls: Operator Overloading

---

## Pitfall 1: Raising `NotImplementedError` in an Operator

Because they sound similar, developers frequently confuse the Exception with the Singleton.

```python
class Vector:
    def __add__(self, other):
        if not isinstance(other, Vector):
            # BUG: This crashes the program!
            raise NotImplementedError 
        return Vector(self.x + other.x)

v = Vector()
# This crashes instantly with an Exception trace.
result = v + (10, 20)
```

**Why it fails:** By raising an exception, you halt the execution engine. Python is supposed to catch `NotImplemented` (the singleton) and try `tuple.__radd__(v)`. By raising the Error, you rob Python of its fallback mechanism.
**Fix:** `return NotImplemented`

---

## Pitfall 2: Mutating `self` inside `__add__`

Infix operators (`+`, `-`, `*`) are universally expected to be immutable operations that produce a brand new value.

```python
class BankAccount:
    def __init__(self, bal):
        self.bal = bal
        
    def __add__(self, other):
        # BUG: __add__ should NEVER mutate self!
        self.bal += other.bal
        return self

a = BankAccount(100)
b = BankAccount(50)
c = a + b

print(a.bal) # 150! We accidentally mutated account A just by evaluating a + b!
```

**Fix:** `__add__` must always return a `BankAccount(self.bal + other.bal)`. Only `__iadd__` is allowed to mutate `self`.

---

## Pitfall 3: Forgetting to `return self` in `__iadd__`

When you write `a += b`, Python evaluates `a = a.__iadd__(b)`.

```python
class Cart:
    def __init__(self):
        self.items = []
        
    def __iadd__(self, item):
        self.items.append(item)
        # BUG: Missing `return self`

c = Cart()
c += "Apple"

print(c) # None! 
```

**Why it fails:** Because `__iadd__` didn't return anything, it implicitly returned `None`. Python then evaluated `c = None`, completely destroying the `Cart` object.
**Fix:** Always write `return self` at the end of augmented assignment methods.
