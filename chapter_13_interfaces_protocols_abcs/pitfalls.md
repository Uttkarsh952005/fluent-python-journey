# Chapter 13 — Pitfalls: Interfaces and ABCs

---

## Pitfall 1: Over-Engineering Custom ABCs

Developers coming from Java or C# often bring "Interface-heavy" architectures into Python. They create a custom `AbstractBaseClass` for every single concept in their application.

```python
import abc

# DON'T DO THIS
class IDatabaseInterface(abc.ABC):
    @abc.abstractmethod
    def connect(self): pass

class ILoggerInterface(abc.ABC):
    @abc.abstractmethod
    def log(self): pass
```

**Why it's a pitfall:** It completely breaks Python's dynamic nature and leads to tightly coupled, rigid code. Luciano Ramalho specifically warns: *“ABCs are meant to encapsulate very general concepts, abstractions... most of the time, your code should just use duck typing or `typing.Protocol`.”*

**Fix:** Use `typing.Protocol` for structural typing without the runtime overhead and rigid inheritance requirements.

---

## Pitfall 2: `NotImplemented` vs `NotImplementedError`

Mixing these two up causes severe, silent bugs in operator overloading and abstract methods.

```python
class Vector:
    def __add__(self, other):
        # BUG: Raising the Exception instead of returning the Singleton
        raise NotImplementedError 
```

**Why it fails:** If you `raise NotImplementedError` in an operator like `__add__`, Python immediately crashes. If you correctly `return NotImplemented`, Python gracefully says "Ah, the left operand doesn't know how to add. Let me ask the right operand by calling its `__radd__`."

**The Rule:**
- **Return** `NotImplemented` in dunder operators (`__eq__`, `__add__`, etc.).
- **Raise** `NotImplementedError` in abstract methods to enforce subclass implementations.

---

## Pitfall 3: Assuming Virtual Subclasses Inherit Code

You can use `MyABC.register(LegacyClass)` to make `isinstance(LegacyClass(), MyABC)` return `True`. 

```python
import collections.abc

class MySequence:
    pass

collections.abc.Sequence.register(MySequence)

s = MySequence()
print(isinstance(s, collections.abc.Sequence))  # True!
```

**The BUG:** A developer might assume that because it is now a `Sequence`, it inherited all the concrete mixin methods of `Sequence` (like `.index()` or `.count()`). **It does not.** Virtual subclasses inherit NO implementation. If you call `s.index()`, it will crash with an `AttributeError`.
