# Chapter 23 — Pitfalls: Attribute Descriptors

---

## Pitfall 1: The Global Storage Trap

This is the most common and devastating mistake when writing descriptors. A descriptor is instantiated as a **Class Attribute**. Therefore, there is only *one* instance of the descriptor per class, shared across thousands of Managed Instances.

```python
class BrokenDescriptor:
    def __set__(self, instance, value):
        # FATAL BUG: 'self' is the descriptor. 
        # If Alice sets her score to 10, Bob's score instantly becomes 10 too!
        self.score = value 
```

**Fix:** You must store the data inside the `instance` (the managed object) so it is isolated.
```python
    def __set__(self, instance, value):
        instance.__dict__[self.storage_name] = value
```

---

## Pitfall 2: Forgetting to handle `instance is None`

When a user tries to inspect the descriptor through the class rather than the instance (e.g., typing `LineItem.weight` instead of `obj.weight`), the `instance` argument passed to `__get__` will be `None`.

```python
class Quantity:
    def __get__(self, instance, owner):
        # BUG: If the user types LineItem.weight, instance is None.
        # This will crash with AttributeError: 'NoneType' object has no attribute '__dict__'
        return instance.__dict__[self.storage_name]
```

**Fix:** `__get__` should always check if `instance is None` and return the descriptor itself, allowing the user to inspect it.
```python
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.storage_name]
```

---

## Pitfall 3: The Non-Overriding Shadow Trap

If your descriptor implements `__get__` but does **not** implement `__set__`, it is a Non-Overriding Descriptor.
If a developer types `obj.my_descriptor = 5`, Python will not throw an error. It will simply create a raw variable `obj.__dict__["my_descriptor"] = 5`. From that moment on, your descriptor is shadowed and will never be called again for that object.
