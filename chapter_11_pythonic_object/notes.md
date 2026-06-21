# Chapter 11: A Pythonic Object — Notes

## 1. Object Representation
Python provides two primary ways for an object to print itself:
*   `__repr__`: Intended for developers. If possible, it should return a string that is a valid Python expression capable of recreating the object (e.g., `Vector2d(3.0, 4.0)`).
*   `__str__`: Intended for end-users. It should be readable and concise (e.g., `(3.0, 4.0)`).

## 2. Formatting via `__format__`
When you use `f"{obj:.2f}"` or `format(obj, '.2f')`, Python calls `obj.__format__('.2f')`. 
If a class does not implement `__format__`, the inherited `object.__format__` simply returns `str(obj)`. 
By implementing `__format__`, you can create custom mini-languages (like adding an `'p'` flag to format vectors as polar coordinates).

## 3. Classmethods vs Staticmethods
*   `@classmethod`: Receives the class itself as the first argument (`cls`). Commonly used for **alternative constructors** (e.g., `dict.fromkeys()`, `datetime.now()`).
*   `@staticmethod`: Receives no implicit first argument. It's essentially a plain module-level function that happens to be housed inside a class body, usually just to group it logically.

## 4. Hashability and Immutability
To use an object as a dictionary key or in a set, it must be **hashable**.
1. It must implement `__hash__()` returning an integer.
2. It must implement `__eq__()`.
3. Its hash value must *never change* during its lifetime.

This means you must make the object's properties read-only (immutable). In Python, this is typically done by storing values in "private" attributes (like `self.__x`) and exposing them via `@property` getters without setters.

## 5. Private Attributes and Name Mangling
Python does not have `private` access modifiers. 
However, if you prefix an attribute with two underscores (e.g., `__x`), Python employs **name mangling**. It automatically renames the attribute to `_ClassName__x`.
This is *not* a security feature to prevent reading the data. It is a safety feature to prevent accidental overriding of internal attributes when someone subclasses your class.

## 6. Saving Space with `__slots__`
By default, Python stores all instance attributes in a highly dynamic dictionary (`__dict__`). Dictionaries have significant memory overhead.
If you have a class that will have millions of instances, you can define `__slots__ = ('x', 'y')`. This tells Python to use a compact, fixed-size C-style array instead of a dictionary.
