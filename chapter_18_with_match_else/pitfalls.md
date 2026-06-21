# Chapter 18 — Pitfalls: Control Flow

---

## Pitfall 1: The Missing `finally` in `@contextmanager`

When using `@contextmanager`, the code before the `yield` is setup, and the code after is teardown. If an exception occurs inside the user's `with` block, the exception is propagated directly out of the `yield` expression inside your generator.

```python
from contextlib import contextmanager

@contextmanager
def lock_manager():
    print("Acquiring lock...")
    yield
    # BUG: If an exception occurs in the with block, this generator
    # crashes at the yield, and the lock is NEVER released!
    print("Releasing lock...")

with lock_manager():
    raise ValueError("Oops!")
```

**Why it fails:** The generator crashes, skipping the rest of its body.
**Fix:** You must always wrap the `yield` in a `try/finally` block.

---

## Pitfall 2: Confusing `for/else` Readability

The keyword `else` on a `for` loop is historically a terrible naming choice. Most programmers intuitively read it as "execute this if the loop didn't run (because the list was empty)". 

```python
results = []
for user in results:
    print(f"Processing {user}")
else:
    # BUG (Logical): Developer thinks this runs because results is empty.
    # It actually runs because the loop completed naturally (without breaking)!
    print("No users found.")
```

**Fix:** Because `for/else` is so counter-intuitive to developers coming from other languages, it is highly discouraged in modern style guides unless it is strictly used with a `break` statement inside the loop (e.g., a search loop where `else` acts as "not found").

---

## Pitfall 3: Wrapping Too Much in `try/except`

A massive anti-pattern is putting code that *should not* be caught into the `try` block.

```python
# BAD
try:
    config = load_json()     # We expect JSONDecodeError here
    run_server(config)       # If this raises JSONDecodeError due to a bug, it gets caught accidentally!
except JSONDecodeError:
    print("Bad config file")

# GOOD
try:
    config = load_json()
except JSONDecodeError:
    print("Bad config file")
else:
    # Only executes if the try succeeded. 
    # Any exception raised here bubbles up properly!
    run_server(config)
```
