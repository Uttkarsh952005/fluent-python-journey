# Chapter 9 — Pitfalls: Decorators and Closures

---

## Pitfall 1: Forgetting `@functools.wraps`

When you write a decorator that replaces a function with a wrapper, the original function's metadata (`__name__`, `__doc__`, and signature) is lost.

```python
def uppercase(func):
    def wrapper(*args, **kwargs):
        """I am the wrapper docstring."""
        return func(*args, **kwargs).upper()
    return wrapper

@uppercase
def greet(name: str):
    """Greets the user."""
    return f"Hello {name}"

print(greet.__name__)  # Prints 'wrapper' (Oops!)
print(greet.__doc__)   # Prints 'I am the wrapper docstring.' (Oops!)
```

**Why it's a disaster:** Frameworks like FastAPI, Flask, and Celery rely heavily on function names, signatures, and docstrings for routing, dependency injection, and schema generation. Losing them breaks the framework.

**Fix:** ALWAYS decorate the inner wrapper with `@functools.wraps(func)`.

---

## Pitfall 2: The `UnboundLocalError` (Accidental Shadowing)

Python decides whether a variable is local or global when the function is compiled. If there is *any* assignment to a variable inside the function, Python considers it a local variable everywhere in that function.

```python
b = 6
def f(a):
    print(a)
    print(b)  # CRASH: UnboundLocalError
    b = 9     # This assignment makes 'b' local for the whole function
```

**Fix:** If you intend to assign to a global variable, use `global b`. If it's a free variable in a closure, use `nonlocal b`.

---

## Pitfall 3: Decorator Side-Effects at Import Time

Because decorators execute when the module is imported, any expensive operations or side-effects placed in the outer decorator function will run immediately at startup.

```python
def connect_to_db_decorator(func):
    # DANGER: This connects to the DB when the module is IMPORTED.
    db = Database.connect("postgres://...") 
    
    def wrapper(*args, **kwargs):
        return func(db, *args, **kwargs)
    return wrapper
```

**Fix:** Only do setup inside the outer decorator if absolutely necessary. Move runtime side-effects inside the inner `wrapper` function.

---

## Pitfall 4: Misusing `@lru_cache` with Unhashable Arguments

`@functools.lru_cache` uses a dictionary under the hood, with the function's arguments acting as the key. Therefore, all arguments passed to a memoized function must be **hashable**.

```python
import functools

@functools.lru_cache()
def process_data(data):
    return sum(data)

# Works fine
process_data((1, 2, 3)) 

# TypeError: unhashable type: 'list'
process_data([1, 2, 3]) 
```

**Fix:** Freeze unhashable arguments (e.g., convert `list` to `tuple`, or `set` to `frozenset`) before passing them into the cached function.
