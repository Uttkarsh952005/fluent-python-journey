# Chapter 8 — Architecture Notes: The Type Hinting System

---

## 1. Type Hints are Purely Static
A core architectural decision of Python's gradual type system (PEP 484) is that it has **zero impact on runtime behavior or optimization**.

Unlike Cython or Java, where declaring an `int` tells the compiler to allocate 4 or 8 bytes of raw memory, Python's `int` type hint is entirely ignored by the CPython bytecode compiler. The interpreter still boxes the integer in a `PyLongObject` struct. Type hints are effectively structural comments.

---

## 2. `__annotations__`
When the Python compiler processes a `def` statement, it parses the type hints and stores them in a dictionary attached to the function object called `__annotations__`.

```python
def f(x: int) -> str: pass
print(f.__annotations__)
# {'x': <class 'int'>, 'return': <class 'str'>}
```

This is the only runtime manifestation of type hints. Frameworks like **Pydantic** and **FastAPI** revolutionized Python web development by reading this `__annotations__` dictionary at runtime to automatically cast JSON payloads and generate OpenAPI schemas.

---

## 3. PEP 563: Postponed Evaluation of Annotations
Historically, type hints were evaluated eagerly. This caused the **Forward Reference Problem**:
```python
class Node:
    # Error: 'Node' is not defined yet!
    def __init__(self, parent: Node): ...
```
To fix this, developers had to wrap the type in a string: `'Node'`.

**PEP 563** introduced `from __future__ import annotations`. When activated, the compiler stops evaluating type hints eagerly and automatically stores them as strings in `__annotations__`.

```python
from __future__ import annotations
def f(x: int) -> str: pass
# f.__annotations__ is now {'x': 'int', 'return': 'str'}
```
This greatly speeds up module import times (because complex generic types aren't instantiated at startup), but shifts the burden to runtime frameworks, which must now use `typing.get_type_hints()` to evaluate the strings safely.

---

## 4. PEP 585: Type Hinting Generics in Standard Collections
Before Python 3.9, the `typing` module contained shadow classes (`typing.List`, `typing.Dict`) that acted as generics. This was because the C-level implementations of `list` and `dict` did not support the `__class_getitem__` method required for the `list[str]` syntax.

PEP 585 implemented `__class_getitem__` on the standard C types, unifying the type hierarchy. 
Now, `list[str]` evaluates at runtime to a `types.GenericAlias` object, removing the need for `typing.List` entirely.
