# Chapter 22: Dynamic Attributes and Properties — Notes

## 1. `__getattr__` vs `__getattribute__`
Understanding the difference is critical for metaprogramming:
*   **`__getattribute__(self, name)`:** Called **unconditionally** every single time an attribute is accessed (`obj.x`). Overriding this is extremely dangerous because if you try to access `self.data` inside it, it will trigger itself, instantly causing a `RecursionError`.
*   **`__getattr__(self, name)`:** The safety net. It is called **only** if the attribute is not found by normal means (i.e., it's not an instance variable and not in the class tree). It is perfectly safe to use for building dynamic wrappers because accessing `self.data` inside it will hit the normal lookup first.

## 2. The Uniform Access Principle
Coined by Bertrand Meyer: *“All services offered by a module should be available through a uniform notation, which does not betray whether they are implemented through storage or through computation.”*
In Python, this is achieved using the `@property` decorator. You can start by exposing a simple raw attribute `obj.balance`. Later, if you need to add validation, you can change it to `@property def balance(self)` without breaking any code that uses your class. 

## 3. `__new__` vs `__init__`
*   `__new__(cls, *args)` is the true constructor. It allocates the memory and returns the newly minted object.
*   `__init__(self, *args)` is the initializer. It receives the object returned by `__new__` and attaches data to it.
When building dynamic factory classes (where you might want to return an instance of a *different* class depending on the input), you must override `__new__`.
