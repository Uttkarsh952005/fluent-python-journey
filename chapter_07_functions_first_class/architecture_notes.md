# Chapter 7 — Architecture Notes: CPython Functions

---

## 1. `PyFunctionObject` vs `PyCodeObject`

In CPython, a function is not a monolithic entity. It is split into two distinct C structs:

### `PyCodeObject`
Generated exactly once during the compilation phase. It is entirely **static** and contains:
- The raw bytecode instructions.
- The names of local variables and arguments.
- Constants used in the code.
- Because it is immutable, it can be safely shared.

### `PyFunctionObject`
Generated at **runtime** when the `def` statement executes. It is the dynamic wrapper around the `PyCodeObject`. It contains:
- `func_code`: Pointer to the static `PyCodeObject`.
- `func_globals`: Pointer to the module dictionary where the function was created.
- `func_defaults`: Default arguments (evaluated at runtime, which is why mutable defaults cause bugs).
- `func_closure`: State captured from enclosing scopes.

When you create a function inside a loop or a factory, CPython reuses the same `PyCodeObject`, but creates a new `PyFunctionObject` to hold the new closure state and defaults.

---

## 2. The `METH_FASTCALL` Optimization

Historically, calling a C-extension function from Python required packing positional arguments into a `tuple` and keyword arguments into a `dict` (using `METH_VARARGS`). Creating and destroying these tuples for every function call added significant overhead.

In Python 3.6, Victor Stinner introduced `METH_FASTCALL`. 
Instead of building a tuple, CPython now passes an **array of pointers** (a C array of `PyObject*`) along with the number of arguments directly to the C function.

### Positional-Only Arguments (`/`)
This is why positional-only arguments (`/`) introduced in Python 3.8 are architecturally important. By explicitly restricting keyword arguments, parsing the function signature becomes incredibly fast. The interpreter can just slice the C-array of pointers directly into local variables, without ever doing expensive dictionary lookups or tuple unpacking.

---

## 3. Why `operator.itemgetter` is Fast

When you run `sorted(data, key=operator.itemgetter(1))`:

1. `itemgetter` returns an object of a specific C-type (`itemgetter_type`).
2. `sorted` is implemented in C.
3. During the C-level quicksort/timsort algorithm, it needs to evaluate the key.
4. Because `itemgetter` is a C-callable, the interpreter executes the data extraction entirely in C.

If you used a `lambda`, CPython would have to instantiate a full Python execution frame, push local variables, run the `BINARY_SUBSCR` bytecode, pop the result, and destroy the frame—*for every single element in the sort*.

---

## 4. `map` and `filter` Laziness in Python 3

In Python 2, `map` and `filter` were eager: `map(str, range(10**6))` immediately allocated a list of 1 million strings.

In Python 3, they return iterator objects (`mapobject` and `filterobject` in C). 
These objects simply store:
- A pointer to the callable.
- A pointer to the underlying iterable.

They execute `PyObject_Call` *only* when `__next__` is invoked. This was a deliberate architectural shift away from lists toward memory-efficient generators, aligning Python more closely with strict functional languages like Haskell (which are lazy by default).
