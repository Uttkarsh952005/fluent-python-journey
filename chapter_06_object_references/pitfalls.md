# Chapter 6 — Pitfalls: Object References, Mutability, and Recycling

---

## Pitfall 1: Expecting Assignment to Copy

```python
a = [1, 2, 3]
b = a           # NOT a copy — just another name for the same list
b.append(4)
print(a)        # [1, 2, 3, 4]  ← surprise!
```

**Fix:** `b = list(a)` or `b = a[:]` for a shallow copy.

---

## Pitfall 2: Using `is` to Compare Values

```python
# WRONG — may work by accident due to interning, but not guaranteed:
if name is "admin":   ...
if count is 0:        ...
if flag is True:      ...   # True is a singleton — this one actually works, but style is bad

# CORRECT:
if name == "admin":   ...
if count == 0:        ...
if flag:              ...   # for booleans, truth test is best
```

`is` checks memory identity. CPython interns small integers (-5 to 256) and some strings, so `is` may appear to work for these — until it doesn't, in production, with different values or a different Python version.

---

## Pitfall 3: Mutable Default Arguments

```python
# BUG — [] is created ONCE at definition time:
def add_item(item, collection=[]):
    collection.append(item)
    return collection

add_item("a")   # ['a']
add_item("b")   # ['a', 'b']  ← 'b' accumulates in the same list!

# FIX:
def add_item(item, collection=None):
    if collection is None:
        collection = []
    collection.append(item)
    return collection
```

---

## Pitfall 4: Shallow Copy Sharing Inner Mutable Objects

```python
import copy

original = [[1, 2], [3, 4]]
shallow  = copy.copy(original)

original[0].append(99)  # mutates inner list
print(shallow[0])       # [1, 2, 99]  ← shallow copy sees the change!
```

**Rule:** Use shallow copy when inner objects are immutable (str, int, tuple). Use `copy.deepcopy()` when inner objects are mutable and you need full independence.

---

## Pitfall 5: Aliasing Function Arguments (TwilightBus Bug)

```python
class Manager:
    def __init__(self, items):
        self.items = items          # BUG: aliasing the caller's list

m = Manager([1, 2, 3])
m.items.remove(1)
# The caller's original list is now [2, 3]!

# FIX: always copy mutable args you intend to own:
class Manager:
    def __init__(self, items):
        self.items = list(items)    # defensive copy
```

---

## Pitfall 6: Relying on `__del__` for Cleanup

```python
class Resource:
    def __del__(self):
        print("cleaning up!")      # may not run when you expect

r = Resource()
del r   # might print immediately in CPython, but NOT in PyPy
```

`__del__` is called when the object is garbage collected — which is immediate in CPython (refcount = 0), but arbitrary in PyPy/Jython (generational GC). **Use context managers (`with` statement) for resource cleanup, not `__del__`.**

---

## Pitfall 7: Tuple's Deceptive Immutability

```python
t = (1, [2, 3])
t[1].append(4)   # works! the tuple's reference didn't change
# t is now (1, [2, 3, 4])

hash(t)          # TypeError — unhashable because inner list is mutable
```

Tuples are immutable at the **reference** level — the references inside can't be rebound. But if a reference points to a mutable object, that object can still change. This is why tuples containing lists can't be dict keys or set members.
