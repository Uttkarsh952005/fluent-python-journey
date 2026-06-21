# Chapter 12 — Architecture Notes: Slices at the C Level

---

## 1. The `slice` Object

In Python, `a:b:c` is syntactic sugar. When used inside square brackets `[a:b:c]`, the CPython parser translates it into a call to the built-in `slice()` function.

```python
# These are evaluated identically by CPython:
my_list[1:10:2]
my_list[slice(1, 10, 2)]
```

At the C level, a `slice` object is a simple struct (`PySliceObject`) containing three PyObject pointers: `start`, `stop`, and `step`. 

---

## 2. The `indices()` Method

One of the trickier parts of slicing is dealing with missing bounds and negative indices (e.g., `[-5:]`). Calculating the actual start and stop integers for an array of a specific length is non-trivial.

To solve this, CPython exposes an `indices(length)` method on `slice` objects.

```python
s = slice(-3, None, None)
print(s.indices(10))  # Output: (7, 10, 1)
```

The `indices()` method takes the length of the target sequence and calculates the exact, positive integer coordinates `(start, stop, step)` needed to execute the slice. It handles negative indices, out-of-bounds indices, and missing steps.

---

## 3. How `__getitem__` Receives Slices

When you write a custom sequence in Python, your `__getitem__` is bound to the C-level `sq_item` or `mp_subscript` slots. 
In Python 3, CPython routes most bracket lookups through `mp_subscript` (the mapping protocol). 

1. User writes `v[1:4]`.
2. CPython parser builds a `slice(1, 4, None)` object.
3. CPython looks up the `__getitem__` method on your class.
4. It passes the `slice` object as the `index` parameter.
5. It is entirely up to the Python-level `__getitem__` method to inspect the type of `index` using `isinstance(index, slice)` and react appropriately.
