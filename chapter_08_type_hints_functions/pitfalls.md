# Chapter 8 — Pitfalls: Type Hints in Functions

---

## Pitfall 1: Over-constraining with `list` or `dict`

The most common beginner mistake is using concrete classes for function parameters.

```python
def print_names(names: list[str]) -> None:
    for name in names:
        print(name)

# A user tries to pass a tuple or a set:
my_set = {"Alice", "Bob"}
print_names(my_set) # Mypy Error: Expected list[str], got set[str]
```
Even though the function only requires iteration (which sets and tuples support), Mypy blocks it because a `set` is not a `list`.

**Fix:** Follow Postel's Law. Use `collections.abc.Iterable`.
```python
from collections import abc
def print_names(names: abc.Iterable[str]) -> None: ...
```

---

## Pitfall 2: Defaulting to `None` without `Optional` / `Union`

If a parameter defaults to `None`, its type is NOT automatically inferred as allowing `None` in strict Mypy mode.

```python
# Mypy Error: Incompatible default for argument "suffix" (default has type "None", argument has type "str")
def add_suffix(word: str, suffix: str = None) -> str:
    if suffix:
        return word + suffix
    return word
```

**Fix:** Use `str | None` (Python 3.10) or `Optional[str]`.
```python
def add_suffix(word: str, suffix: str | None = None) -> str: ...
```

---

## Pitfall 3: `Any` is contagious

Using `Any` silences the type checker, but it also strips type safety from any variable that touches it.

```python
from typing import Any

def get_data() -> Any:
    return {"key": "value"}

# The type of `data` becomes `Any`.
data = get_data()

# Mypy allows this, but it will crash at runtime!
result = data.append("bug") 
```

**Fix:** If you don't know the exact type, use `object` instead of `Any`. The type checker will force you to use `isinstance()` checks before calling methods on it.

---

## Pitfall 4: Type aliases vs `NewType`

If you use a simple variable assignment for an alias, Mypy treats them as completely interchangeable.

```python
UserId = int

def get_user(id: UserId) -> str: ...

# This is completely valid to Mypy, even though it's semantically wrong.
score = 100
get_user(score)
```

**Fix:** If you want strict semantic separation without runtime overhead, use `NewType`.
```python
from typing import NewType

UserId = NewType('UserId', int)

def get_user(id: UserId) -> str: ...

score = 100
get_user(score)  # Mypy Error: Expected UserId, got int
```
