# Chapter 16: Operator Overloading — Notes

## 1. The Immutability Rule of Operators
A fundamental rule of Python operator overloading: Infix operators like `+` (`__add__`) and `*` (`__mul__`) must **never** mutate their operands. They must always read from the operands and return a **new object**.

## 2. The Operator Dispatch Mechanism
When Python evaluates `a + b`, it follows this exact sequence:
1. Call `a.__add__(b)`.
2. If `__add__` raises an exception, crash.
3. If `__add__` returns `NotImplemented`, or if `a` has no `__add__` method, Python calls `b.__radd__(a)`.
4. If `__radd__` returns `NotImplemented`, or if `b` has no `__radd__` method, Python raises a `TypeError: unsupported operand type(s) for +`.

This mechanism is what allows `(1, 2) + MyVector([3, 4])` to work, even though the built-in `tuple` class has no idea what `MyVector` is.

## 3. `NotImplemented` vs `NotImplementedError`
*   `NotImplemented` is a singleton value (like `None`). You **return** it from dunder operator methods to tell Python's execution engine to try the reverse fallback.
*   `NotImplementedError` is an exception. You **raise** it inside abstract base classes to force subclasses to override a method. If you raise it inside an operator method, it breaks the dispatch chain and crashes the program.

## 4. Augmented Assignment (`+=`)
Augmented assignment operators like `+=` look for the in-place method `__iadd__`.
*   If `__iadd__` exists, Python evaluates `a = a.__iadd__(b)`. The method *should* mutate `a` in place, and it **must** `return self`.
*   If `__iadd__` does not exist, Python falls back to `a = a.__add__(b)`. This evaluates the expression and binds the variable `a` to the brand new object returned by `__add__`.
