# Chapter 22 — Pitfalls: Dynamic Attributes

---

## Pitfall 1: Hiding Expensive Operations behind Properties

The Uniform Access Principle dictates that properties (`obj.data`) and methods (`obj.get_data()`) should feel the same to the developer.
However, developers psychologically expect an attribute access (`obj.data`) to be instantaneous. 

```python
class ServerNode:
    @property
    def is_active(self):
        # BUG (Architectural): Hiding a 2-second network request behind a property!
        # Developers typing `if node.is_active` will freeze their UI without warning.
        response = requests.get(f"http://{self.ip}/ping")
        return response.status_code == 200
```

**Fix:** If a calculation is computationally heavy or requires I/O (network/database), it **must** be a method (`obj.is_active()`). If it is static but expensive, use `@functools.cached_property` so it only hurts once.

---

## Pitfall 2: Infinite Recursion in `__getattribute__`

If you override `__getattribute__` instead of `__getattr__`, Python will call it for **every single attribute lookup**.

```python
class BadObject:
    def __init__(self):
        self.data = {"id": 1}

    def __getattribute__(self, name):
        # FATAL: To get `self.data`, Python calls `__getattribute__("data")`.
        # Which hits `self.data`, which calls `__getattribute__("data")`...
        # Crashes instantly with RecursionError.
        return self.data[name]
```

**Fix:** Use `__getattr__` (which only runs if the attribute is missing). If you *must* use `__getattribute__`, you must retrieve attributes via the superclass: `return super().__getattribute__("data")[name]`.

---

## Pitfall 3: Failing to Override `dir()`

If you dynamically generate attributes using `__getattr__`, standard Python tools like `dir(obj)` or `help(obj)` will not see them, making debugging a nightmare.

**Fix:** If you implement `__getattr__`, you should also implement `__dir__(self)` to return a list of all your dynamically generated keys.
