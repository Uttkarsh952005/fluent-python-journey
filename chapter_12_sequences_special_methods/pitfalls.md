# Chapter 12 — Pitfalls: Sequences and Dynamic Attributes

---

## Pitfall 1: The `__getattr__` Infinite Recursion Bug

`__getattr__` is called when an attribute lookup **fails**. If your `__getattr__` implementation references an attribute that *also* doesn't exist on `self`, it triggers another call to `__getattr__`. This loops infinitely until Python crashes with a `RecursionError`.

```python
class BrokenRoute:
    def __getattr__(self, name):
        # BUG: If self.target isn't defined in __init__, this 
        # triggers __getattr__('target'), which triggers 
        # __getattr__('target')... infinitely!
        return self.target.get(name)
```

**Fix:** Ensure any attribute referenced inside `__getattr__` is definitively created in `__init__`, or use `super().__getattribute__` to bypass fallback lookup.

---

## Pitfall 2: The Shadowing Vulnerability

Because `__getattr__` only fires when an attribute is missing from the instance `__dict__`, it is highly vulnerable to "shadowing." If a user assigns a value to a dynamic attribute, it gets written to `__dict__`. From then on, `__getattr__` is silenced for that name.

```python
class Vector:
    def __init__(self):
        self._data = [10, 20]
        
    def __getattr__(self, name):
        if name == 'x': return self._data[0]

v = Vector()
print(v.x)  # 10 (via __getattr__)

v.x = 99    # Puts 'x' in v.__dict__
print(v.x)  # 99 (Reads from dict, bypassing __getattr__)
```

**Fix:** If you implement `__getattr__` for dynamic properties, you **must** implement `__setattr__` to block assignment to those specific names.

---

## Pitfall 3: Returning Native Types from Slices

If you build a custom sequence (e.g., a `TimeSeries` or a custom `Vector`), developers expect a slice of that sequence to return a smaller instance of the *same type*. A common mistake is to return a native list or array instead.

```python
class Deck:
    def __init__(self, cards):
        self.cards = cards
        
    def __getitem__(self, index):
        # BUG: If index is a slice, this returns a native list!
        return self.cards[index]

d = Deck(['Ace', 'King', 'Queen'])
hand = d[0:2]
print(type(hand))  # <class 'list'> — We lost the Deck type!
```

**Fix:** Check if `index` is a slice, and wrap the result back in `type(self)`.

```python
    def __getitem__(self, index):
        cls = type(self)
        if isinstance(index, slice):
            return cls(self.cards[index])  # Returns a new Deck!
        return self.cards[index]
```
