# Chapter 15 — Pitfalls: Advanced Type Hints

---

## Pitfall 1: Assuming `typing.cast` does Runtime Validation

A critical mistake developers make when coming from strongly typed languages (like C++ or Java) is assuming that `cast()` performs validation or data coercion.

```python
from typing import cast, TypedDict

class User(TypedDict):
    id: int
    name: str

raw_payload = {"id": "Not an int", "name": "Admin"}

# BUG: Developer assumes this validates the dictionary. It does not.
safe_user = cast(User, raw_payload)

# This will completely crash downstream when we try to do math on the ID!
print(safe_user['id'] + 10)  # TypeError: can only concatenate str to str
```

**Why it fails:** `cast` literally does nothing at runtime. It just tells Mypy: "Trust me, this is a `User`." If you lie, Mypy will blindly approve it, and the bug will explode in production.
**Fix:** If you need runtime validation, use a library like `Pydantic`. Use `cast` only when you (the developer) know something Mypy physically cannot infer.

---

## Pitfall 2: The `@overload` Logic Trap

Because decorators normally wrap function logic, it is highly unintuitive that `@overload` throws logic away.

```python
from typing import overload, Any

@overload
def parse(val: str) -> str:
    # BUG: Developer puts logic here.
    return val.strip()

@overload
def parse(val: list) -> list:
    # BUG: Developer puts logic here.
    return [v.strip() for v in val]

# The final concrete implementation
def parse(val: Any) -> Any:
    return val
```

**Why it fails:** Python's module parsing evaluates functions from top to bottom. The final `def parse` simply overwrites the previous two in the module's `__dict__`. When you call `parse("  hello  ")`, it returns `"  hello  "`, totally ignoring your `strip()` logic.

**Fix:** Overloaded function bodies must be empty (using `...` or `pass`). ALL runtime logic must go in the single, final concrete function, utilizing `isinstance` checks to branch the logic.
