# Chapter 24 — Architecture Notes: CPython Class Construction

---

## 1. The Dual Nature of `type`

`type` is the most unique construct in Python. It is both a class *and* an object.
*   It is an instance of itself: `type(type) == type`
*   It inherits from object: `issubclass(type, object) == True`
*   `object` is an instance of `type`: `type(object) == type`

This creates the core foundation of Python's object model: everything inherits from `object`, but everything is built by `type`.

---

## 2. The 5-Step Class Creation Sequence

When CPython reads a class definition during Evaluation Time, it executes a highly specific sequence:

```python
class MyModel(BaseModel, metaclass=CustomMeta):
    data = 5
    def do_work(self): pass
```

1.  **Metaclass Discovery:** Python looks for `metaclass=` in the class signature. If none exists, it checks the parent classes. If none exist, it defaults to `type`.
2.  **Prepare Namespace:** Python calls `CustomMeta.__prepare__(name, bases)`. This returns an empty dictionary. (In advanced cases, it returns an `OrderedDict` to preserve attribute declaration order).
3.  **Evaluate Body:** Python executes the code *inside* the class block. `data = 5` and the `do_work` function are loaded into the dictionary returned by Step 2.
4.  **Metaclass `__new__`:** Python calls `CustomMeta.__new__(CustomMeta, "MyModel", (BaseModel,), dict_from_step_3)`. This physically allocates the memory for the new Class Object.
5.  **`__init_subclass__`:** After the class is fully built, Python scans its parent classes (`BaseModel`) and calls their `__init_subclass__` methods, allowing the parent to react to the newly born child.

---

## 3. Class Decorators vs Metaclasses

A Class Decorator executes *after* Step 5.
```python
@add_timestamp
class MyModel: pass

# Under the hood, this is literally just:
MyModel = add_timestamp(MyModel)
```

Because it happens after Step 5, you cannot intercept or prevent the creation of the class. If the class definition was invalid, the memory was already allocated and the time was already wasted. A Metaclass (Step 4) intercepts the process *before* the memory is allocated.
