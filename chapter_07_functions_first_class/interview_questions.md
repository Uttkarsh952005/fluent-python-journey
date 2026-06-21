# Chapter 7 — Interview Questions: Functions as First-Class Objects

---

## 🟢 L3

### Q1: What makes a function "first-class" in Python?
It means a function is treated like any other object in the language (like an `int` or a `list`). Specifically, it can be:
1. Created at runtime.
2. Assigned to a variable or data structure.
3. Passed as an argument to another function.
4. Returned as the result of a function.

---

### Q2: Why are list comprehensions generally preferred over `map` and `filter` in modern Python?
1. **Readability:** Comprehensions read closer to natural language and don't require defining throwaway `lambda` functions.
2. **Performance:** For simple operations, comprehensions avoid the overhead of calling a Python function (the lambda) for every single element, executing entirely in C at the bytecode level.

```python
# map/filter
list(map(lambda x: x.upper(), filter(lambda x: len(x)>5, words)))

# listcomp
[x.upper() for x in words if len(x)>5]
```

---

## 🟡 L4

### Q3: How do you make an instance of a custom class behave like a function?
By implementing the `__call__` magic method. Any object with a `__call__` method is recognized as "callable" by the `callable()` built-in. This is useful for creating function-like objects that need to maintain internal state between calls (e.g., rate limiters, caches).

```python
class Counter:
    def __init__(self):
        self.count = 0
    def __call__(self):
        self.count += 1
        return self.count

c = Counter()
c() # returns 1
```

---

### Q4: Explain the difference between positional-only (`/`) and keyword-only (`*`) parameters.
- `/` indicates that all parameters *before* it must be supplied positionally. They cannot be passed as keywords. (Added in Python 3.8 to match C-level functions like `divmod()`).
- `*` indicates that all parameters *after* it must be passed as keyword arguments. They cannot be passed positionally.

```python
def f(pos_only, /, standard, *, kw_only): pass
f(1, standard=2, kw_only=3) # Valid
```

---

## 🔴 L5

### Q5: What does `functools.partial` do, and why not just use a `lambda` to wrap arguments?
`functools.partial(func, *args, **kwargs)` creates a new callable with some arguments pre-filled (frozen).
While a `lambda` can achieve the same result (`lambda x: func(10, x)`), `partial` is preferred because:
1. **Performance:** `partial` is implemented in C and is heavily optimized.
2. **Introspection:** `partial` objects expose `.func`, `.args`, and `.keywords` attributes, allowing frameworks to inspect the original function. Lambdas obscure this.
3. **Safety:** It avoids the "late binding" trap common when creating lambdas inside loops.

---

### Q6: Why is `operator.itemgetter(1)` faster than `lambda x: x[1]` when used as a sorting key?
`operator.itemgetter` is implemented entirely in C. When passed as a key to `sorted()` (which is also implemented in C), the entire sorting loop executes without ever needing to transition back into the Python bytecode evaluation loop to execute a function. 

A `lambda`, on the other hand, is a proper Python function. Calling it requires creating a Python frame, binding arguments, executing bytecode, and returning—adding significant overhead inside a tight sorting loop.

---

## 🟣 L6

### Q7: If functions are objects, what class are they an instance of, and how are they represented in CPython memory?
Functions are instances of the `function` class (accessible via `types.FunctionType`). 

In CPython, they are represented by the `PyFunctionObject` C struct. This struct holds pointers to various components that make up the function, such as:
- `func_code`: Pointer to the `PyCodeObject` containing the compiled bytecode.
- `func_globals`: Pointer to the dictionary of global variables where the function was defined.
- `func_defaults`: Tuple of default positional arguments.
- `func_kwdefaults`: Dict of default keyword arguments.
- `func_closure`: Tuple of cell objects for variables captured from outer scopes.

This separation of the *function* (runtime context) from the *code* (static bytecode) is what allows closures and multiple instantiations of the same function body to exist efficiently.
