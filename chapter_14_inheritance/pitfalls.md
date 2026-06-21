# Chapter 14 — Pitfalls: Inheritance and MRO

---

## Pitfall 1: Subclassing Native `dict` or `list`

If you override `__setitem__` on a `dict` subclass, your override will NOT be called when you initialize the dict or when you call `update()`.

```python
class BlockedDict(dict):
    def __setitem__(self, key, val):
        if key == 'admin': raise ValueError("Blocked!")
        super().__setitem__(key, val)

# This works (intercepted by Python)
d = BlockedDict()
d['user'] = 1

# BUG: This completely bypasses __setitem__!
d.update({'admin': 1})
print(d)  # {'user': 1, 'admin': 1} — The block failed!
```

**Why it fails:** The C-level implementation of `dict.update()` calls the C dictionary assignment function directly. It does not pause to evaluate `self.__class__.__dict__['__setitem__']` in Python space for every key.

**Fix:** Inherit from `collections.UserDict`, which is implemented in Python and specifically designed to route all operations through the standard dunder methods.

---

## Pitfall 2: The Missing `super()` Chain (The Black Hole)

In a multiple inheritance hierarchy, every class in the MRO must call `super().__init__()` (or the equivalent method) to pass control to the next class in the chain. If even one class forgets, the chain stops.

```python
class MixinA:
    def execute(self):
        print("MixinA running")
        # BUG: Forgot super().execute()!

class MixinB:
    def execute(self):
        print("MixinB running")

class System(MixinA, MixinB):
    def execute(self):
        super().execute()

s = System()
s.execute() 
# Output: "MixinA running"
# MixinB NEVER runs, because MixinA swallowed the delegation!
```

---

## Pitfall 3: Failing to Accept `**kwargs` in Cooperative `__init__`

When you have a diamond inheritance structure, you often do not know which class `super().__init__()` will resolve to. If your `__init__` only accepts specific arguments, the chain will eventually crash with a `TypeError`.

```python
class A:
    def __init__(self, name):
        self.name = name
        # BUG: A doesn't accept **kwargs, so it can't pass them to B!
        super().__init__()

class B:
    def __init__(self, age):
        self.age = age
        super().__init__()

class C(A, B):
    def __init__(self, name, age):
        # TypeError: A.__init__() got an unexpected keyword argument 'age'
        super().__init__(name=name, age=age) 
```

**Fix:** Every class designed for cooperative multiple inheritance must accept `**kwargs` and pass them unconditionally to `super().__init__(**kwargs)`.
