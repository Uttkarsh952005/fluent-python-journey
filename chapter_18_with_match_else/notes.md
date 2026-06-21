# Chapter 18: with, match, and else Blocks — Notes

## 1. Context Managers (`with`)
The `with` statement exists to abstract away the standard `try/finally` pattern for resource management (closing files, releasing locks, rolling back transactions).
It relies on two dunder methods:
*   `__enter__(self)`: Prepares the resource. What it returns is bound to the `as` variable (e.g., `with open() as f:` binds the file object to `f`).
*   `__exit__(self, exc_type, exc_val, traceback)`: Tears down the resource. If the `with` block completes successfully, all three arguments are `None`. If an exception is raised inside the block, they contain the exception details.
    *   **CRITICAL RULE:** If `__exit__` returns `True`, the exception is swallowed. If it returns `None` (or `False`), the exception propagates.

## 2. `@contextlib.contextmanager`
Writing full classes for simple teardown operations is verbose. The `@contextmanager` decorator allows you to use a generator instead.
```python
@contextmanager
def manage_resource():
    print("Setup")
    try:
        yield resource  # Halts here and runs the 'with' block body
    finally:
        print("Teardown")
```
If an exception occurs inside the `with` block, it is injected back into the generator right at the `yield` statement. If you do not have a `try/finally` block, your generator will crash and the teardown code will never execute.

## 3. `else` Blocks on Loops
In Python, `else` can be attached to `for` and `while` loops. 
*   **Meaning:** "Execute the `else` block if and only if the loop completed naturally without hitting a `break`."
*   **Use Case:** Searching for an item. If you loop through a list and `break` when you find it, the `else` block acts as your "Item not found" fallback.

## 4. `try/except/else/finally`
*   `except`: Runs if an exception occurred.
*   **`else`:** Runs if **NO** exception occurred inside the `try` block. It is the proper place to put code that should only execute if the `try` succeeded, without wrapping that extra code inside the `try` block itself (which might mask unrelated bugs).
*   `finally`: Runs no matter what.
