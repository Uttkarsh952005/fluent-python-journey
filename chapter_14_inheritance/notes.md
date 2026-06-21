# Chapter 14: Inheritance: For Better or For Worse — Notes

## 1. The Built-in Subclassing Trap
**Never subclass C-level built-ins (`dict`, `list`, `str`) directly if you intend to override their behavior.**
*   **Why?** The C implementations of these classes take shortcuts. A C-level `dict.update()` does not execute Python-level method lookups. It directly calls the C-level dictionary assignment logic, completely bypassing any `__setitem__` you have overridden in Python.
*   **The Fix:** Always subclass `collections.UserDict`, `collections.UserList`, or `collections.UserString`. These are written in pure Python and guarantee that all internal calls route properly through your overridden methods.

## 2. Method Resolution Order (MRO)
Python supports multiple inheritance. To resolve which method to call, Python uses the **C3 Linearization Algorithm** to build a flat list of classes called the `__mro__`.
*   The MRO guarantees that a subclass always precedes its superclasses.
*   If a class inherits from multiple classes (e.g., `class Leaf(A, B)`), `A` will precede `B` in the MRO.
*   If the inheritance graph is impossible to linearize without violating these rules, Python raises a `TypeError` at class creation time.

## 3. What `super()` Actually Does
A common misconception is that `super()` means "call my parent class." 
**This is completely false in multiple inheritance.**
`super()` means: "Look at the `__mro__` of the current *instance* `self`, find where the *current executing class* is in that list, and delegate the call to the **next** class in the list."
This is cooperative multiple inheritance. It prevents "diamond problems" where a base class's `__init__` is called twice.

## 4. Best Practices for Mixins
A Mixin is a class designed to be combined with other classes via multiple inheritance. It provides specific functionality (like logging or serialization) but is not meant to be instantiated on its own.

**Rules for Mixins:**
1.  Name them with a `Mixin` suffix (e.g., `JSONRendererMixin`).
2.  Mixins should not have an `__init__` method if possible, or if they do, they *must* accept `**kwargs` and call `super().__init__(**kwargs)`.
3.  A Mixin should only bundle related methods; it should not hold primary state.
4.  When defining a concrete class, the Mixins should come *first* in the inheritance list, followed by the primary base class: `class WebRequest(LoggingMixin, JSONMixin, BaseRequest):`
