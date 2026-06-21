# Chapter 8: Type Hints in Functions — Notes

## 1. Gradual Typing
Python is dynamically typed and will remain so. PEP 484 introduced a **gradual type system**, similar to TypeScript.
- **Optional**: Type hints are ignored by the Python interpreter at runtime.
- **No Performance Gain**: The CPython bytecode compiler does not optimize based on type hints. They exist solely for static analysis tools like Mypy and IDEs.

## 2. Duck Typing vs. Nominal Typing
- **Duck Typing (Runtime)**: Cares only about supported operations. If it walks like a duck, it is a duck. Flexible, but errors happen at runtime.
- **Nominal Typing (Static)**: Relies on declared class names and inheritance structures. A type checker checks the source code statically. A subclass is `consistent-with` its superclass, but a structurally identical class without inheritance is rejected.

## 3. Postel's Law (The Robustness Principle)
> *"Be conservative in what you send, be liberal in what you accept."*

When annotating functions:
- **Accept** Abstract Base Classes (`abc.Mapping`, `abc.Sequence`, `abc.Iterable`).
- **Return** concrete classes (`dict`, `list`).

This prevents over-constraining your callers. If you demand a `list`, the caller can't pass a `tuple` or a `deque`, even if your function only iterates over it. Demand an `abc.Iterable` instead.

## 4. `Any` vs `object`
- `Any`: The "wildcard" type. It sits at both the top and bottom of the type hierarchy. You can assign anything to it, and it assumes **every operation is valid**. Using `Any` disables type checking for that variable.
- `object`: Sits only at the top. You can assign anything to it, but it assumes **almost no operations are valid** (it doesn't have `__mul__`, `__add__`, etc.).

## 5. Type Hinting Syntax Cheat Sheet (Python 3.10+)

| Intent | Type Hint | Example |
|--------|-----------|---------|
| List of strings | `list[str]` | `['a', 'b']` |
| Variable length tuple | `tuple[int, ...]` | `(1, 2, 3)` |
| Tuple as Record | `tuple[str, int, float]` | `('Tokyo', 36, 139.6)` |
| Dictionary | `dict[str, int]` | `{'age': 30}` |
| String or None | `str \| None` (was `Optional[str]`) | `"hello"` or `None` |
| Int or Float | `int \| float` (was `Union[int, float]`) | `1` or `2.5` |
| Accepts any iterable | `abc.Iterable[str]` | list, set, tuple of str |
