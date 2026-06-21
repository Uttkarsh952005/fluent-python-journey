# Chapter 9 — Architecture Notes: Closures and Cell Objects

---

## 1. Fast Locals vs. Cell Objects

In CPython, local variables are heavily optimized. They are stored in an array on the C call stack, and accessed via extremely fast `LOAD_FAST` and `STORE_FAST` bytecode instructions using index numbers rather than dictionary lookups.

When a variable is identified as a **free variable** (meaning it is defined in an outer function and used in an inner closure), CPython can no longer safely keep it on the fast local stack. When the outer function returns, its stack frame is destroyed. If the inner closure was returned and outlives the outer function, the variable would be lost.

To solve this, CPython promotes free variables to **Cell Objects** (allocated on the heap).

---

## 2. The `__closure__` Attribute

A function object in Python has a `__closure__` attribute. For normal functions, this is `None`. For closures, it is a tuple of `cell` objects.

```python
def make_averager():
    count = 0
    total = 0.0
    def averager(new_value):
        nonlocal count, total
        count += 1
        total += new_value
        return total / count
    return averager

avg = make_averager()
print(avg.__closure__)
# (<cell at 0x...: int object at 0x...>, <cell at 0x...: float object at 0x...>)
```

The outer function's local scope and the inner function's `__closure__` tuple both point to the *exact same* cell objects. When `avg()` updates `count` using `nonlocal`, it is mutating the value reference *inside* the cell. 

---

## 3. Bytecode Analysis (`LOAD_DEREF`)

Because free variables live in cells, CPython uses different bytecode instructions to access them.

- **Local variables:** `LOAD_FAST`, `STORE_FAST`
- **Global variables:** `LOAD_GLOBAL`, `STORE_GLOBAL`
- **Free variables:** `LOAD_DEREF`, `STORE_DEREF`

When the compiler emits `LOAD_DEREF`, it instructs the interpreter: "Don't look in the local stack array, and don't look in the globals dictionary. Go to the `__closure__` tuple, get the cell at index N, and dereference the value inside it."

---

## 4. `functools.lru_cache` Internals

The `@lru_cache` decorator is a masterclass in closure optimization. Under the hood (in its C implementation), it maintains:
- A `dict` mapping the function arguments to the computed results.
- A **doubly linked list** to track the "Least Recently Used" order.

When you call an `@lru_cache` decorated function:
1. It creates a tuple from the arguments to use as a hash key.
2. It does a fast dictionary lookup.
3. If it's a hit, it updates the doubly linked list (moving the node to the front) and returns the value.
4. If it's a miss, it calls the original function, stores the result, and if `maxsize` is reached, it drops the tail of the linked list and removes that key from the dictionary.
