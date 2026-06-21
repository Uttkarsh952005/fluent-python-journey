# Chapter 23 — Architecture Notes: Method Binding

---

## 1. Functions are Descriptors!

One of the most profound architectural revelations in Python is that **methods do not technically exist**. There are only functions, and functions are Non-Overriding Descriptors.

Every `def` function in Python implements `__get__`.

```python
class MyClass:
    def greet(self):
        return "Hello"

obj = MyClass()
```

When you type `obj.greet`, Python follows the standard lookup chain (Chapter 22). It doesn't find `greet` in the instance dictionary, so it looks at the class dictionary. It finds a function object. Because the function object has a `__get__` method, Python invokes it:

`function.__get__(instance=obj, owner=MyClass)`

---

## 2. The Bound Method Wrapper

What does the function's `__get__` actually return?
It does not return the function itself. It returns a **Bound Method** object.

A bound method is essentially a partial function. It holds a reference to the original function, and a reference to `obj`.
When you add parentheses to call it: `obj.greet()`, the Bound Method executes the original function, automatically injecting the `obj` reference as the very first argument. This is exactly how `self` gets populated!

```python
# What you type:
obj.greet()

# What Python's descriptor protocol actually executes:
bound_method = MyClass.__dict__['greet'].__get__(obj, MyClass)
bound_method() 
# Inside bound_method(): -> original_function(obj)
```

---

## 3. `staticmethod` and `classmethod`

These decorators are just built-in Descriptors that override the default function `__get__` behavior!

*   `@staticmethod`: Its `__get__` method simply returns the raw, original function without wrapping it in a bound method. Therefore, `self` is never injected.
*   `@classmethod`: Its `__get__` method returns a bound method, but instead of binding the `instance` (obj), it binds the `owner` (the Class itself) to the first argument (`cls`).
