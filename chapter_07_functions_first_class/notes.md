# Chapter 7: Functions as First-Class Objects — Notes

## 1. The "First-Class" Definition
In programming language theory, a first-class entity can be:
1. Created at runtime
2. Assigned to a variable or data structure
3. Passed as an argument to a function
4. Returned as the result of a function

In Python, **all functions are first-class objects**. They are instances of the `function` class.

## 2. Higher-Order Functions
A function that takes a function as an argument or returns one is a **higher-order function**.
- `map(func, iterable)`
- `filter(predicate, iterable)`
- `reduce(func, iterable)`
- `sorted(iterable, key=func)`

### Modern Alternatives
In modern Python (3.x), `map` and `filter` are usually better expressed using **list comprehensions** or **generator expressions**:
```python
# Old functional style
list(map(factorial, filter(lambda n: n % 2, range(6))))

# Modern Pythonic style
[factorial(n) for n in range(6) if n % 2]
```

## 3. The 9 Flavors of Callables
You can check if an object is callable using the built-in `callable()` function.

| Type | Created By | Description |
|------|------------|-------------|
| **User-defined functions** | `def` or `lambda` | Standard functions |
| **Built-in functions** | C implementation | e.g., `len`, `time.strftime` |
| **Built-in methods** | C implementation | e.g., `dict.get` |
| **Methods** | Class definition | Functions bound to objects |
| **Classes** | `class` statement | Calling a class runs `__new__` then `__init__` |
| **Class instances** | Class instantiation | Callable if class defines `__call__` |
| **Generator functions** | `yield` keyword | Returns a generator object |
| **Native coroutines** | `async def` | Returns a coroutine object |
| **Async generators** | `async def` + `yield` | Returns an async generator |

## 4. Anonymous Functions (`lambda`)
Python limits `lambda` bodies to a **single pure expression** (no statements, no assignments, no `while`/`try`).

**Fredrik Lundh's Refactoring Recipe:**
1. Write a comment explaining what the lambda does.
2. Think of a name that captures that essence.
3. Convert the lambda to a `def` using that name.
4. Remove the comment.

*Rule of thumb: If a lambda is hard to read, convert it to a `def`.*

## 5. Advanced Parameter Signatures

| Syntax | Name | Meaning |
|--------|------|---------|
| `def f(a, /, b)` | Positional-only | `a` must be positional. (Python 3.8+) |
| `def f(a, *, b)` | Keyword-only | `b` must be passed as `b=value`. |
| `def f(*args)` | Var positional | Captures extra positional args as a tuple. |
| `def f(**kwargs)`| Var keyword | Captures extra keyword args as a dict. |

## 6. Functional Primitives

### `operator` Module
Replaces trivial lambdas with optimized C implementations:
- Arithmetic: `mul`, `add`, `sub`
- Item retrieval: `itemgetter(1)` (replaces `lambda x: x[1]`)
- Attribute retrieval: `attrgetter('name')` (replaces `lambda x: x.name`)
- Method calling: `methodcaller('upper')` (replaces `lambda x: x.upper()`)

### `functools.partial`
Freezes some arguments of a callable, producing a new callable with a simpler signature. Useful for adapting APIs that expect callbacks with fewer arguments.
```python
from functools import partial
from operator import mul

# Create a function that multiplies by 3
triple = partial(mul, 3)
triple(7) # 21
```
