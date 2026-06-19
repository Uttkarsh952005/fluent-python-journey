# Chapter 1 — Notes: The Python Data Model

## Core Concept: The Data Model as a Framework

Python's data model is **not** a feature — it's the *meta-architecture* of the entire language. It defines how objects integrate with:
- Built-in functions (`len`, `abs`, `bool`, `repr`)
- Operators (`+`, `*`, `in`, `[]`)
- Language statements (`for`, `if`, `with`, `del`)

## Key Special Method Families

### Sequence Protocol
| Method | Triggers |
|--------|---------|
| `__len__` | `len(obj)` |
| `__getitem__` | `obj[key]`, `obj[start:stop]`, `for x in obj` (fallback) |
| `__setitem__` | `obj[key] = value` |
| `__delitem__` | `del obj[key]` |
| `__contains__` | `item in obj` (falls back to `__getitem__` scan) |
| `__iter__` | `for x in obj`, `iter(obj)` |
| `__reversed__` | `reversed(obj)` |

### Numeric Protocol
| Method | Triggers |
|--------|---------|
| `__add__` | `a + b` |
| `__radd__` | `b + a` (when b doesn't know how to add a) |
| `__iadd__` | `a += b` |
| `__mul__` | `a * b` |
| `__abs__` | `abs(a)` |
| `__neg__` | `-a` |
| `__pos__` | `+a` |

### Representation Protocol
| Method | Triggers |
|--------|---------|
| `__repr__` | `repr(obj)`, REPL output, `f"{obj!r}"` |
| `__str__` | `str(obj)`, `print(obj)`, `f"{obj}"` |
| `__format__` | `format(obj, spec)`, `f"{obj:spec}"` |
| `__bytes__` | `bytes(obj)` |

### Comparison & Hashing
| Method | Triggers |
|--------|---------|
| `__eq__` | `a == b` |
| `__lt__` | `a < b` |
| `__hash__` | `hash(obj)`, using as dict key |
| `__bool__` | `bool(obj)`, `if obj:`, `while obj:` |

## Critical Rules

### 1. `__repr__` is mandatory; `__str__` is optional
If `__str__` is missing, Python falls back to `__repr__`. So always implement `__repr__`.
`__repr__` should ideally return a string that could reconstruct the object: `Vector(3, 4)` not `"vector at 0x..."`.

### 2. `__eq__` implies `__hash__` rules
- Define `__eq__` without `__hash__` → object becomes **unhashable** (can't use in sets/dicts)
- If `__eq__` compares by value, `__hash__` must hash the same fields: `hash((self.x, self.y))`
- Mutable objects should NOT be hashable (no `__hash__`)

### 3. Return `NotImplemented` not `NotImplementedError`
When a binary operator can't handle the other type:
```python
def __add__(self, other):
    if not isinstance(other, MyClass):
        return NotImplemented  # ← correct: a sentinel value
    ...
```
This lets Python try the reflected operator on the other object. `NotImplementedError` is an exception for abstract methods.

### 4. `__bool__` fallback chain
```
bool(obj)
  → __bool__?  → return bool result
  → __len__?   → return len(obj) != 0
  → True        (default: all objects are truthy)
```

## Vocabulary

| Term | Meaning |
|------|---------|
| **Special method / dunder** | Methods like `__len__` called by Python internally |
| **Protocol** | Informal interface defined by which special methods you implement |
| **Duck typing** | Python checks what an object *can do*, not what it *is* |
| **Structural typing** | Type compatibility via structure (methods), not inheritance |
| **Nominal typing** | Type compatibility via explicit type declaration (Java, C#) |
