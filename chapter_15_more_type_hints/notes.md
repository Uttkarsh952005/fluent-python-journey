# Chapter 15: More About Type Hints — Notes

## 1. `@typing.overload`
Python functions cannot be overloaded at runtime like in Java. If you write `def foo(a: int)` and then `def foo(a: str)`, the second definition simply overwrites the first one in the module's `__dict__`.
However, you can use `@overload` to provide **static signatures** for Mypy.
*   You write multiple empty functions marked with `@overload`.
*   You write one final, concrete function *without* the decorator.
*   Mypy uses the overloaded signatures to validate calls.
*   Python ignores the overloaded bodies completely and only executes the concrete function.

## 2. `typing.TypedDict`
A standard Python `dict` is totally unstructured. A `dataclass` is structured but carries runtime overhead (it creates a real class, an `__init__`, etc).
`TypedDict` is the perfect middle ground.
*   It tells Mypy exactly what keys and value types a dictionary must contain.
*   At runtime, **it completely vanishes**. Calling `MyTypedDict(a=1)` returns a native `dict`.
*   It is the standard way to enforce type safety on parsed JSON payloads.

## 3. `typing.cast(type, obj)`
Static type checkers sometimes fail to infer types correctly, especially when data crosses system boundaries (e.g. `json.loads()`).
`cast(TargetType, my_obj)` is a directive that tells Mypy: "Ignore what you think this is, and treat it as `TargetType`."
*   **WARNING:** It is dangerous. If you lie to the type checker, Mypy will approve the code, but Python will crash at runtime.
*   At runtime, `cast()` literally does nothing. Its implementation in `typing.py` is literally `def cast(typ, val): return val`.

## 4. `typing.TypeVar` (Generics Refresher)
When writing functions that operate on containers, use `TypeVar` to tie the input type to the output type.
```python
T = TypeVar('T')
def first(iterable: Iterable[T]) -> T: ...
```
This tells Mypy: whatever type goes into the iterable, is the exact type that comes out.
