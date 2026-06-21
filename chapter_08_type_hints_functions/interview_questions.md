# Chapter 8 — Interview Questions: Type Hints in Functions

---

## 🟢 L3

### Q1: Does Python run faster if you add type hints?
No. CPython ignores type hints entirely at runtime. They have exactly zero impact on bytecode execution speed. Their sole purpose is to feed data to static analysis tools like Mypy and IDE autocompletion engines to catch bugs before execution.

---

### Q2: How do you indicate that a parameter is optional?
By assigning it a default value.
*Note:* The `Optional` type hint (or `| None`) does **not** make a parameter optional. It simply tells the type checker that `None` is a valid argument. 

```python
# 'name' is NOT optional here, you must pass it (e.g. hello(None)).
def hello(name: str | None): pass 

# 'name' IS optional here.
def hello(name: str | None = None): pass 
```

---

## 🟡 L4

### Q3: What is the difference between Duck Typing and Nominal Typing?
- **Duck Typing (Runtime Python):** Doesn't care what the object's class is named. It only checks if the object supports the method or property being called at runtime.
- **Nominal Typing (Mypy/Static Checkers):** Looks strictly at the class name and inheritance tree. If a function expects a `Bird`, and you pass a `Dog` that happens to have a `.fly()` method, nominal typing will reject it, even if it would succeed at runtime.

---

### Q4: Explain "Postel's Law" in the context of type hints.
"Be conservative in what you send, be liberal in what you accept."
- For function parameters (what you accept), use broad Abstract Base Classes like `abc.Iterable` or `abc.Mapping`.
- For return values (what you send), use concrete types like `list` or `dict`.
This gives callers maximum flexibility while giving consumers concrete guarantees.

---

## 🔴 L5

### Q5: What is the difference between annotating a parameter as `Any` versus `object`?
- `Any`: Disables type checking. The type checker assumes the object supports **every** possible method and attribute. It is "consistent-with" everything.
- `object`: The base class of all classes. The type checker assumes the object supports **almost nothing** (only base methods like `__str__` and `__eq__`). It forces you to write `isinstance` checks before using the object.

---

### Q6: How do you type hint a callback function?
Using `typing.Callable`. The syntax takes a list of argument types and a return type: `Callable[[Arg1Type, Arg2Type], ReturnType]`.

```python
from typing import Callable

def register(callback: Callable[[str, int], bool]) -> None:
    pass
```

---

## 🟣 L6

### Q7: Explain what PEP 585 changed in Python 3.9 regarding generics.
Before Python 3.9, you had to import capitalized types from the `typing` module to annotate collections (e.g., `from typing import List, Dict`). 

PEP 585 allowed the standard built-in collections (`list`, `dict`, `set`, `tuple`) and ABCs (`collections.abc.Sequence`) to support generic subscripting directly. You can now write `list[str]` without importing anything. This unified the runtime classes with the static type hint markers, deprecating `typing.List` etc.

---

### Q8: What is the runtime introspection difference between `__annotations__` and `typing.get_type_hints()`?
At runtime, `func.__annotations__` is a simple dictionary mapping parameter names to exactly what was written in the source code.

`typing.get_type_hints(func)` is a heavily engineered function that:
1. Resolves forward references (types written as strings).
2. Follows the MRO to resolve annotations inherited from base classes.
3. Resolves stringified annotations if `from __future__ import annotations` (PEP 563) is used in the module.

Because `get_type_hints` has to evaluate these references, it introduces significant runtime overhead compared to reading `__annotations__`.
