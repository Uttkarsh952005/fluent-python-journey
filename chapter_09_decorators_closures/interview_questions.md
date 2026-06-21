# Chapter 9 — Interview Questions: Decorators and Closures

---

## 🟢 L3

### Q1: What is a decorator in Python?
A decorator is a function that takes another function as an argument and extends or alters its behavior without explicitly modifying its source code. In Python, `@decorator` is syntactic sugar for `func = decorator(func)`.

---

### Q2: When is a decorator executed?
A decorator is executed at **import time** (when the Python script is parsed and loaded into memory). The function it wraps is executed later, at **runtime**, when explicitly called.

---

## 🟡 L4

### Q3: What is a closure?
A closure is a dynamically generated function that remembers the state of the environment in which it was created. Specifically, it retains bindings to **free variables** (variables defined in the outer enclosing function) even after the outer function has finished executing.

---

### Q4: When do you need to use the `nonlocal` keyword?
When you have a nested function (a closure) and you want to **reassign** a free variable defined in the outer function. If you only want to *read* the free variable, or mutate it in place (like appending to a list), you don't need `nonlocal`. You only need it for the `=` assignment operator, to prevent Python from creating a new local variable that shadows the outer one.

---

## 🔴 L5

### Q5: How do you write a decorator that accepts arguments? (e.g., `@retry(retries=3)`)
You need a "decorator factory"—a function that takes the arguments and returns the actual decorator. This requires three levels of nested functions:
1. The factory (takes the arguments, returns the decorator)
2. The decorator (takes the function, returns the wrapper)
3. The wrapper (takes `*args, **kwargs`, executes the logic and calls the function).

---

### Q6: What does `@functools.wraps` do, and why is it important?
When a decorator replaces a function with a wrapper, the original function's identity (its `__name__`, `__doc__` docstring, and parameter signature) is lost and replaced by the wrapper's identity. `@wraps` is a decorator applied to the inner wrapper function that copies all this metadata from the original function to the wrapper. It is vital for debugging, introspection, and frameworks that rely on signatures.

---

## 🟣 L6

### Q7: Explain how CPython implements closures under the hood.
When CPython compiles a function and detects that an inner function references a variable from an outer function, it creates a **Cell Object**. 
Instead of storing the variable's value on the fast local call stack, it stores a reference to this cell object. Both the outer function and the inner closure contain pointers to this same cell. The inner function's bytecode uses the `LOAD_DEREF` instruction to access the value inside the cell. You can inspect these cells at runtime using the function's `__closure__` attribute.
