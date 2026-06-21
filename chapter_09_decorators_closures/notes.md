# Chapter 9: Decorators and Closures — Notes

## 1. When do decorators execute?
Decorators execute at **import time** (when the module is loaded). This is why registration decorators (like `@app.route` in Flask or `@singledispatch`) work instantly when the script starts. The *decorated function*, however, only runs when explicitly called at **runtime**.

## 2. Variable Scope and UnboundLocalError
When Python compiles a function, it decides variable scope:
1. If a variable is assigned a value inside the function, it is deemed **local**.
2. If it is only read, it is deemed a **global** or **free variable**.

If you try to read a local variable before it is assigned, you get an `UnboundLocalError`.

```python
b = 6
def f(a):
    print(a)
    print(b)  # UnboundLocalError!
    b = 9     # Because of this assignment, Python classifies `b` as local.
```

## 3. Closures
A closure is a function with an extended scope that encompasses **free variables** (variables that are neither global nor local, but bound in an outer enclosing function).
- If you only *read* a free variable in a closure, you don't need special syntax.
- If you need to *re-assign* a free variable, you must use the `nonlocal` keyword to prevent Python from shadowing it as a local variable.

## 4. `functools.wraps`
When you write a decorator that returns an inner wrapper function, the wrapper takes on the name and docstring of the inner function (e.g., `__name__` becomes `'wrapper'`).
Always use `@functools.wraps(func)` on the inner function to copy `__name__`, `__doc__`, and signature metadata from the original function.

## 5. Standard Library Highlights
- `@functools.lru_cache(maxsize=128)`: Memoizes the results of a function. Requires arguments to be hashable.
- `@functools.singledispatch`: Transforms a normal function into a single-dispatch generic function, allowing you to overload the function based on the type of its first argument.

## 6. Parameterized Decorators
To pass arguments to a decorator (e.g., `@retry(max_attempts=3)`), you need a **decorator factory**.
This requires 3 layers of nested functions:
1. The **Factory** (takes the parameters, returns the Decorator)
2. The **Decorator** (takes the function, returns the Wrapper)
3. The **Wrapper** (takes the args/kwargs, executes the function)
