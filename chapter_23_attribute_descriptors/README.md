# Chapter 23 — Attribute Descriptors

> **Theme**: Descriptors are the mechanism that makes Python's `@property`, `@classmethod`, `staticmethod`, and even regular methods work. By implementing the descriptor protocol, you can extract complex validation logic out of properties and into highly reusable classes.

## What You'll Learn

| Concept | Explanation |
|---------|------------|
| **Descriptor Protocol** | Any class that implements `__get__`, `__set__`, or `__delete__`. |
| **Overriding Descriptor** | Implements `__set__`. Cannot be shadowed by an instance variable. |
| **Non-Overriding Descriptor** | Implements only `__get__`. Can be silently overwritten by assigning to `obj.attr`. |
| **`__set_name__`** | Called automatically upon class creation so the descriptor knows its own variable name. |

## Key Files

- [`examples.py`](examples.py) — Building the `Quantity` Overriding Descriptor to automatically enforce `>0` validation across multiple attributes.
- [`exercises.py`](exercises.py) — Proving the Global Storage trap (why descriptors must save data into `instance.__dict__` instead of `self.data`).
- [`mini_project.py`](mini_project.py) — A simulated Django ORM, demonstrating how `models.CharField` abstracts type checking and length validation completely away from the main class definition.
- [`benchmarks.py`](benchmarks.py) — Proving that Descriptors incur zero extra memory overhead on the instances compared to `@property` definitions.
- [`notes.md`](notes.md) — The strict nomenclature required to understand descriptors.
- [`pitfalls.md`](pitfalls.md) — Shadowing traps and `__get__` signature errors.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — The profound revelation that standard Python functions are actually Non-Overriding descriptors, which is how `self` gets magically bound to methods.

## 30-Second Rules

```python
# Rule 1: Descriptors must be instantiated as CLASS attributes, never inside __init__.
class Model:
    # GOOD
    data = Descriptor()

# Rule 2: Descriptors must ALWAYS store their data in the managed instance!
def __set__(self, instance, value):
    # BAD: Shares data across all Model instances
    self.data = value 
    
    # GOOD: Stores data specifically for this object
    instance.__dict__[self.storage_name] = value

# Rule 3: Always implement __set_name__ in modern Python (3.6+).
def __set_name__(self, owner, name):
    self.storage_name = name
```

*Reference: Fluent Python 2nd ed., Chapter 23 — pages 907–945*
