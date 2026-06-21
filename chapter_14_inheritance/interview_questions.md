# Chapter 14 — Interview Questions: Inheritance and MRO

---

## 🟢 L3

### Q1: Why is subclassing `dict` or `list` directly considered dangerous in Python?
Because `dict` and `list` are implemented in C. To optimize performance, their internal C-level methods often call other C-level methods directly, completely bypassing any overrides you write in Python. For example, if you override `__setitem__` on a `dict` subclass, `dict.update()` will ignore your override.

### Q2: How do you safely subclass built-in collections?
Instead of subclassing `dict`, `list`, or `str` directly, subclass `UserDict`, `UserList`, or `UserString` from the `collections` module. These classes are written in pure Python, meaning they are guaranteed to route all internal operations through the standard dunder methods you can override.

---

## 🟡 L4

### Q3: What is a Mixin class? Give an example.
A Mixin class is a class designed to provide specific functionality (like logging, serialization, or validation) to other classes through multiple inheritance. It is not meant to be instantiated on its own. 
Example: Django's `LoginRequiredMixin`. You apply it to a View class (`class DashboardView(LoginRequiredMixin, TemplateView):`) to mix in authentication checks without writing a rigid inheritance hierarchy.

### Q4: In `class C(A, B):`, if both `A` and `B` implement a `process()` method, which one gets called by `C().process()`?
Python resolves this using the Method Resolution Order (MRO). Because `A` is listed before `B` in the class signature, `A` will precede `B` in the `__mro__`. Therefore, `A.process()` will be called.

---

## 🔴 L5

### Q5: Does `super()` always call the parent class?
No! This is a very common misconception. In multiple inheritance, `super()` delegates to the **next class in the MRO**. 
For example, in a diamond graph where `Leaf` inherits from `A` and `B` (which both inherit from `Root`), calling `super().ping()` from inside `A.ping()` will actually call `B.ping()`, not `Root.ping()`. It acts cooperatively, passing control sideways across the inheritance graph to ensure every class gets called exactly once.

---

## 🟣 L6

### Q6: What is the C3 Linearization Algorithm? What problem does it solve?
C3 Linearization is the algorithm Python uses to compute the `__mro__`. It guarantees three properties:
1. **Local precedence order:** If `class C(A, B)` is declared, `A` will always come before `B` in the MRO.
2. **Monotonicity:** A subclass always comes before its base classes.
3. **Consistency:** If a class appears before another class in one MRO, it must appear before that class in all other MROs in the hierarchy.

If these constraints are impossible to satisfy (e.g. `A` inherits from `B`, but a subclass inherits from `B` then `A`), the algorithm fails and Python raises a `TypeError` at class compilation time, preventing impossible diamond problems.
