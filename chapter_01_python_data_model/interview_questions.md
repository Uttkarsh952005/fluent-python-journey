# Chapter 1 — Interview Questions: The Python Data Model

> Questions ranging from L3 (junior/mid) to L6 (staff engineer) level.
> Each answer includes the depth expected at a senior Python interview.

---

## 🟢 L3 — Junior / Entry Level

### Q1: What are "dunder methods" and why does Python use them?

**Expected answer:**
Dunder methods (double-underscore methods like `__len__`, `__add__`) are Python's mechanism for letting user-defined classes integrate with built-in language constructs. They're called by the Python interpreter in response to operations like `len()`, `+`, or `in`.

Python uses this design (rather than requiring inheritance from a base class) to support **duck typing**: you don't need to declare "I am a Sequence" — you just implement `__len__` and `__getitem__` and Python treats you as one.

---

### Q2: What's the difference between `__repr__` and `__str__`?

**Expected answer:**
- `__repr__`: Developer-facing. Should be unambiguous, ideally reconstructable. Called by `repr()`, the REPL, and `f"{obj!r}"`. If `__str__` is absent, `str()` falls back to `__repr__`.
- `__str__`: User-facing. Should be readable and concise. Called by `print()`, `str()`, and `f"{obj}"`.

**Rule of thumb**: Always implement `__repr__`. Implement `__str__` only when the user representation should differ from the debug representation.

---

## 🟡 L4 — Mid-Level

### Q3: Why does Python's `len()` function exist when objects could just have a `.length` attribute?

**Expected answer:**
Several reasons:
1. **Consistency**: `len()` works uniformly on strings, lists, dicts, custom objects. A `.length` attribute would be inconsistent (is it `.length`, `.size`, `.count`?).
2. **C-level optimization**: For built-in types, `len()` directly accesses the C-level `ob_size` field or `tp_as_sequence->sq_length`. This is ~50ns — faster than any Python attribute lookup.
3. **Protocol enforcement**: `len()` validates the return value (must be non-negative int). A raw attribute has no such guarantee.
4. **Pythonic design**: "There should be one obvious way to do it."

---

### Q4: What happens when Python evaluates `a + b`?

**Expected answer:**
Python's binary operator dispatch:
1. Call `type(a).__add__(a, b)`
2. If that returns `NotImplemented`, call `type(b).__radd__(b, a)`
3. If that also returns `NotImplemented`, raise `TypeError`

Special case: if `type(b)` is a **subclass** of `type(a)`, Python tries `type(b).__radd__` first. This lets subclasses override behavior even when they appear on the right side.

---

### Q5: Why can't you put a list in a Python set or use it as a dict key?

**Expected answer:**
Sets and dict keys require objects to be **hashable** — meaning they must implement `__hash__`. Lists are mutable: you can append, remove, or reorder elements. If a list's hash changed while it was stored in a set, the set would look in the wrong hash bucket and never find it again.

Python's contract: **if two objects compare equal (`==`), they must have the same hash**. This invariant breaks for mutable objects — so lists, dicts, and sets are intentionally unhashable.

Tuples are hashable (if their elements are hashable) because they're immutable.

---

## 🔴 L5 — Senior

### Q6: Explain how `bool(obj)` works when `__bool__` is not defined.

**Expected answer:**
Python checks a fallback chain:
1. `__bool__` defined? → call it, return the result
2. `__len__` defined? → call it; `True` if `len(obj) > 0`, else `False`
3. Neither defined? → `True` (all objects are truthy by default)

This has a subtle implication: if your class implements `__len__` but not `__bool__`, it inherits truthiness from its size. An empty custom collection becomes falsy automatically — which is often the right behavior (mirrors `list`, `dict`, etc.).

**Performance note**: The `__bool__` path is ~20–30% faster than the `__len__` fallback because Python doesn't need to call `len()` and compare against zero.

---

### Q7: What is the difference between `NotImplemented` and `NotImplementedError`?

**Expected answer:**
- `NotImplemented` is a **singleton sentinel value** (like `None`). It's returned from binary operator methods to signal "I don't know how to handle this type — let Python try the reflected operator."
- `NotImplementedError` is an **exception**, raised from abstract methods to signal "this method must be implemented by a subclass."

Returning `NotImplementedError` from `__add__` is a bug — it stops Python from trying the reflected operator and immediately propagates the error up.

```python
def __add__(self, other):
    if not isinstance(other, MyType):
        return NotImplemented        # ✅ Let Python try other.__radd__
        # NOT: raise NotImplementedError()  ❌
```

---

## 🟣 L6 — Staff Engineer / Python Internals

### Q8: How does CPython implement `len()` for built-in types vs user-defined classes?

**Expected answer:**
In CPython, every type has a `PyTypeObject` struct that contains pointers to C functions implementing various operations. For sequences, `tp_as_sequence->sq_length` is this pointer.

For built-in list: `len([1,2,3])` → `PyObject_Size()` → `Py_TYPE(o)->tp_as_sequence->sq_length(o)` → returns `ob_size` directly. This is one C function call — no Python dispatch, no attribute lookup.

For user-defined classes: `len(obj)` → `PyObject_Size()` → no `sq_length` slot → falls through to Python-level `__len__` dispatch via `_PyObject_LookupSpecial`. This involves: type lookup, attribute access, and a Python function call — roughly 3–5x slower than the built-in path.

This explains why `len(list)` is ~50ns while `len(UserClass)` is ~90ns.

---

### Q9: Python makes mutable objects unhashable by default when `__eq__` is defined. Why is this a conservative but correct choice?

**Expected answer:**
When you define `__eq__`, Python sets `__hash__ = None`. The rationale: Python cannot know whether your object is safe to hash after you've defined custom equality. If your `__eq__` uses mutable fields and you allow hashing, objects could end up in the wrong bucket after mutation — causing silent data corruption in sets and dicts.

The conservative default forces you to explicitly opt into hashability by implementing `__hash__`, which forces you to think about: "which fields should determine the hash? Are those fields immutable?"

This design follows the principle: **it's better to fail loudly (TypeError: unhashable) than silently corrupt data**.

---

*These questions test not just Python knowledge but systems thinking and understanding of WHY Python is designed the way it is.*
