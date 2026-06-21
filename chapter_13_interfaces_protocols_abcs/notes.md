# Chapter 13: Interfaces, Protocols, and ABCs — Notes

## 1. Three Kinds of Interfaces in Python

| Approach | Type | Enforced At | Inherits From | Description |
|----------|------|-------------|---------------|-------------|
| **Duck Typing** | Dynamic | Runtime | `object` | "If it walks like a duck." Works blindly at runtime. Crashes if the method is missing. |
| **Goose Typing** | Dynamic | Runtime | `abc.ABC` | Explicitly subclassing an Abstract Base Class. Fails early (at instantiation) if methods are missing. |
| **Static Duck Typing**| Static | Pre-runtime | `object` | Typing hints using `typing.Protocol`. Validates structural compatibility via Mypy before the code ever runs. |

## 2. Abstract Base Classes (ABCs)
*   Found in `collections.abc` and `numbers`.
*   You use them to verify interfaces at runtime (`isinstance(obj, abc.MutableSequence)`).
*   **Rule of Thumb:** You should *subclass* existing ABCs frequently. You should almost *never* create your own custom ABCs unless you are building a massive framework (like Django or Pytest). Custom ABCs introduce rigid coupling.

## 3. `typing.Protocol`
*   Introduced in PEP 544.
*   It solves the "Static Duck Typing" problem. If you want Mypy to verify that an object has a `.read()` method, you don't force the object to inherit from `ReaderABC` (which forces tight coupling). Instead, you define a `Protocol` with a `.read()` method, and Mypy checks if the object structurally matches it.

## 4. `NotImplemented` vs `NotImplementedError`
These sound identical but are completely different:
*   `NotImplemented` is a **singleton** (like `None`). It is *returned* (not raised) by special methods like `__eq__` or `__add__` to tell Python: "I don't know how to handle this, try asking the other operand."
*   `NotImplementedError` is an **exception**. It is *raised* in abstract methods to tell the subclass: "You forgot to implement this method!"

## 5. Virtual Subclasses
You can bypass inheritance entirely using `MyABC.register(MyClass)`. 
This is called a **virtual subclass**. `isinstance(MyClass(), MyABC)` will return `True`, but Python will NOT check if the methods actually exist, nor will `MyClass` inherit any mixin methods from the ABC. It is a pure "trust me" mechanism.
