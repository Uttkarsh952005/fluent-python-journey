# Chapter 12: Special Methods for Sequences — Notes

## 1. The Sequence Protocol
In Python, you do not need to inherit from `abc.Sequence` to be a sequence. You only need to implement:
*   `__len__`
*   `__getitem__`

If you implement these two methods, Python automatically grants you:
*   Iteration (`for x in obj`)
*   Reversal (`reversed(obj)`)
*   The `in` operator (`x in obj`)

## 2. Slice Awareness
When a user does `obj[1:4]`, Python passes a `slice` object to `__getitem__`.
A robust sequence must handle this explicitly. Instead of returning a native list or array, a slice operation should ideally return a **new instance of the same class**.

```python
def __getitem__(self, index):
    if isinstance(index, slice):
        return type(self)(self._components[index]) # Return a new Vector
```

## 3. Dynamic Attributes (`__getattr__`)
*   `__getattr__` is called as a **fallback** ONLY when an attribute lookup fails in the instance `__dict__` and the class tree.
*   If you implement `__getattr__` to allow dynamic access (e.g., `v.x` routing to `v[0]`), you **must** also implement `__setattr__`.
*   Why? Because if a user does `v.x = 10`, it bypasses `__getattr__` and creates a real `x` in the `__dict__`. From then on, `v.x` will return 10 instead of dynamically fetching `v[0]`. This is called **shadowing**.

## 4. Hashing N-Dimensional Objects
To hash a tuple, Python hashes every element and combines them using a bitwise XOR. We can replicate this efficiently for N-dimensional objects using `functools.reduce` and `operator.xor`.

```python
def __hash__(self):
    # Hash each component, then XOR them all together
    hashes = map(hash, self._components)
    return functools.reduce(operator.xor, hashes, 0)
```

## 5. Efficient Equality (`__eq__`)
When comparing two large sequences, creating a massive tuple in memory `tuple(self) == tuple(other)` is wasteful.
Instead, use `zip()` combined with a generator expression and `all()`. Because `all()` short-circuits, it will stop evaluating the moment it finds a mismatch.

```python
def __eq__(self, other):
    if len(self) != len(other):
        return False
    return all(a == b for a, b in zip(self, other))
```
