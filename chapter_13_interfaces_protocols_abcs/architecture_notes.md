# Chapter 13 — Architecture Notes: `isinstance` and `__subclasshook__`

---

## 1. The Cost of `isinstance` against an ABC

Standard inheritance checks in Python are highly optimized C-level operations. If you check `isinstance(obj, MyClass)`, CPython simply traverses the `__mro__` (Method Resolution Order) tuple of `obj.__class__`.

However, checking `isinstance(obj, abc.Sized)` is significantly heavier.

Because `collections.abc.Sized` is an Abstract Base Class powered by the `ABCMeta` metaclass, it overrides the default `__instancecheck__` and `__subclasscheck__` mechanisms.

---

## 2. The `__subclasshook__`

When you evaluate `isinstance(obj, abc.Sized)`, the `ABCMeta` metaclass intercepts the check and looks for a special class method called `__subclasshook__` on `Sized`.

The `Sized` ABC implements it roughly like this:

```python
class Sized(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Sized:
            if any("__len__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
```

### The CPython Execution Path:
1. Python calls `Sized.__instancecheck__(obj)`.
2. This triggers `Sized.__subclasshook__(obj.__class__)`.
3. The hook dynamically iterates through the entire `__mro__` of the target class.
4. It checks the `__dict__` of every class in the MRO to see if the string `"__len__"` exists.
5. If found, it returns `True`, and the `isinstance` check passes—even if the object did not inherit from `Sized`.

---

## 3. Architectural Takeaway

The `__subclasshook__` is what enables "Goose Typing." It allows standard `isinstance()` checks to dynamically verify structure (duck typing) instead of just checking rigid inheritance trees (nominal typing). 

However, because this involves multiple Python-level function calls, MRO traversals, and dictionary lookups, **`isinstance` against an ABC is ~4x slower than a simple `hasattr` check.** Use it at architectural boundaries where safety is more important than microsecond performance.
