# Chapter 15 — Architecture Notes: `typing` at Runtime

---

## 1. The Implementation of `typing.cast`

One of the most surprising things about the `typing` module is how trivial some of its functions are at runtime.

If you look at the actual CPython source code for `typing.py`, the implementation of `cast` is exactly this:

```python
def cast(typ, val):
    """Cast a value to a type.
    This returns the value unchanged.  To the type checker this
    signals that the return value has the designated type, but at
    runtime we intentionally don't check anything (we want this
    to be as fast as possible).
    """
    return val
```

Because of this, `cast` carries a microscopic function-call overhead, but absolutely no validation overhead. It is purely a syntactic marker for Mypy.

---

## 2. The Implementation of `TypedDict`

When you define a `TypedDict` using class syntax:

```python
class Point(TypedDict):
    x: int
    y: int
```

At runtime, `Point` is actually parsed by the `_TypedDictMeta` metaclass. 
The metaclass strips away all the type hints and stores them in `Point.__annotations__`.
When you call `Point(x=1, y=2)`, the metaclass intercepts the instantiation and simply returns a native Python `dict(x=1, y=2)`.

This means `type(Point(x=1, y=2))` is strictly `<class 'dict'>`. The `Point` class vanishes completely from the instance's MRO. This is why `TypedDict` has zero runtime overhead compared to `dict`, making it significantly faster to build millions of JSON objects than a `dataclass`.

---

## 3. `get_type_hints()` vs `__annotations__`

Why do we use `typing.get_type_hints(obj)` instead of just reading `obj.__annotations__`?

Since PEP 563 (Postponed Evaluation of Annotations), type hints are often stored as pure strings in the `__annotations__` dictionary rather than evaluated class objects.
`get_type_hints()` resolves those strings dynamically by evaluating them against the module's globals and locals namespace. It also walks the MRO to merge annotations from base classes. Reading `__annotations__` directly is fragile and heavily discouraged.
