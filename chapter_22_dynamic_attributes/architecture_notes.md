# Chapter 22 — Architecture Notes: Property Lookups

---

## 1. The Standard Lookup Chain

When you evaluate `obj.name` in CPython, the interpreter does not simply look in one place. It follows a strict hierarchical chain:
1.  **Data Descriptors:** Does the class (or its superclasses) have an attribute called `name` that implements `__get__` and `__set__`? (This is what `@property` creates!). If so, use it.
2.  **Instance Dictionary:** Does `obj.__dict__['name']` exist? If so, return it.
3.  **Non-Data Descriptors:** Does the class have an attribute called `name` that only implements `__get__`? (Like standard methods or `@cached_property`). If so, use it.
4.  **Class Dictionary:** Does `type(obj).__dict__['name']` exist? If so, return it.
5.  **`__getattr__`:** If all the above fail, and the class defines `__getattr__`, call it.
6.  **AttributeError:** If `__getattr__` doesn't exist or raises `AttributeError`, crash.

---

## 2. The `@property` Override

Because Data Descriptors (Step 1) are checked *before* the Instance Dictionary (Step 2), a `@property` completely overrides any actual instance variable of the same name.

```python
class Test:
    @property
    def data(self):
        return "Protected"

t = Test()
t.__dict__["data"] = "Hacked!"
print(t.data) # Still prints "Protected"!
```
Even if you manually inject `"data"` into the instance dictionary, the `@property` catches the lookup at Step 1 and intercepts it.

---

## 3. The `@cached_property` Exploit

Introduced in Python 3.8, `@cached_property` is a **Non-Data Descriptor**. It only implements `__get__`.
Because it does not implement `__set__`, it falls to Step 3 in the lookup chain.

When `obj.data` is accessed the first time:
1. Step 1 fails.
2. Step 2 fails (it's not in `__dict__` yet).
3. Step 3 hits the `cached_property`. It runs the calculation. It saves the answer via `obj.__dict__['data'] = answer` and returns it.

When `obj.data` is accessed the second time:
1. Step 1 fails.
2. Step 2 **SUCCEEDS**. It finds the cached answer directly in the `__dict__` and returns it in O(1) time. The `cached_property` method is never called again!
