# Chapter 6 — Architecture Notes: Reference Semantics Internals

---

## CPython Object Structure

Every Python object starts with a common C header:

```c
typedef struct _object {
    Py_ssize_t ob_refcnt;   /* reference count */
    PyTypeObject *ob_type;  /* pointer to type object */
} PyObject;
```

`ob_refcnt` is the reference count. Every `INCREF` increments it; every `DECREF` decrements it. When it reaches 0, `tp_dealloc` is called — the object is immediately freed.

This is why CPython object destruction is deterministic and fast: no GC pause, no delay. The object dies the moment the last reference is released.

---

## What Triggers a INCREF / DECREF

| Operation | Effect |
|-----------|--------|
| `x = obj` | INCREF on `obj` |
| `del x` | DECREF on `obj` |
| Function argument passed | INCREF |
| Function returns | DECREF on local variables |
| List append / dict insert | INCREF |
| List remove / dict delete | DECREF |
| `x = other_obj` (rebind) | DECREF on old `obj`, INCREF on `other_obj` |

---

## Why Reference Counting Fails for Cycles

```
Object A:  ob_refcnt = 1 (referenced by B.attr)
Object B:  ob_refcnt = 1 (referenced by A.attr)
```

If no external names point to A or B, they're unreachable. But neither refcount reaches 0 — so they're never freed. This is a **reference cycle memory leak**.

CPython's solution (added in 2.0): a **generational garbage collector** (GC) that runs periodically and finds unreachable cycles.

---

## CPython Generational GC

Objects are tracked in 3 generations:
- **Generation 0**: new objects (checked most frequently)
- **Generation 1**: survived one GC round
- **Generation 2**: long-lived objects (checked rarely)

The GC scans all objects in a generation, counts references that come from *within* the generation, and finds objects whose external references have dropped to 0. These are the unreachable cyclic garbage.

```python
import gc
gc.get_threshold()   # (700, 10, 10)
# Gen 0 collected after 700 new objects allocated since last collection
# Gen 1 collected after 10 gen-0 collections
# Gen 2 collected after 10 gen-1 collections
```

---

## `del` Semantics

`del x` does **not** delete the object. It:
1. Removes the binding of name `x` from the current namespace
2. Calls `DECREF` on the object
3. If the refcount hits 0 → object is destroyed

```python
a = [1, 2, 3]
b = a
del a           # DECREF: refcount 2 → 1. Object still alive.
del b           # DECREF: refcount 1 → 0. Object destroyed NOW.
```

---

## Interning: How Python Deduplicates Immutables

CPython maintains interning tables for:
- **Small integers**: -5 to 256 — permanently cached, always the same object
- **Strings**: identifier-like strings interned at compile time; others optionally via `sys.intern()`
- **Tuples**: `tuple(t)` where `t` is already a tuple returns the same object (no copy)
- **frozenset**: `fs.copy()` returns the same object — a documented "harmless lie"

```python
# Integer interning:
a = 256; b = 256; a is b   # True  (cached)
a = 257; b = 257; a is b   # False (not cached)

# String interning:
s = sys.intern("my string")   # force interning
```

**Why interning is safe for immutables**: Two equal immutable objects can safely share identity because their value will never change. If `a == b` for immutables, making `a is b` is a valid optimization with no observable behavioral difference.

---

## Weak References: References That Don't Count

A **weak reference** holds a reference to an object but does NOT increment its refcount. The object can be garbage collected even while a weak ref exists — when that happens, the weak ref becomes "dead" (returns `None`).

```python
import weakref

cache: dict[str, weakref.ref] = {}

obj = SomeExpensiveObject()
cache["key"] = weakref.ref(obj)

# Later:
retrieved = cache["key"]()   # call the ref to get the object
if retrieved is None:
    # Object was garbage collected — rebuild it
    ...
```

**Use cases**:
- Caches that don't prevent GC of cached objects
- Observer patterns — listeners don't keep subjects alive
- `weakref.WeakValueDictionary` — values automatically removed when collected

---

## The `__copy__` and `__deepcopy__` Protocol

You can customize copy behavior by implementing:

```python
class MyClass:
    def __copy__(self):
        # return a shallow copy
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo: dict):
        # memo maps id(original) → copy, prevents cycles
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result    # register BEFORE recursing to handle cycles
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result
```

The `memo` dict is critical — it's what prevents infinite loops when deepcopying cyclic structures.
