# Chapter 10 — Architecture Notes: Bound Methods as Commands

---

## 1. The Heavy Object-Oriented Command Pattern

In a strict OOP language without first-class functions, implementing the Command Pattern requires significant architectural overhead:

1. **Receiver**: The object that does the actual work.
2. **Command Interface**: An interface dictating an `execute()` method.
3. **Concrete Command**: A class that implements the interface, takes the Receiver in its constructor, saves it as a private field, and calls the receiver's method inside `execute()`.
4. **Invoker**: The object that holds the Concrete Command and calls `.execute()`.

Every single command requires a brand-new class definition.

---

## 2. Python's Implicit Command Pattern (`types.MethodType`)

Python's architecture natively implements the Command pattern every time you access a method on an instance.

Consider this code:
```python
class Light:
    def turn_on(self):
        print("Light is on")

light = Light()
cmd = light.turn_on  # Creating the command
cmd()                # Executing the command
```

When you type `light.turn_on` (without parentheses), CPython does not return the raw function. It invokes the Descriptor Protocol, which returns a **Bound Method Object** (implemented in C as `PyMethod_Type`).

### Inside the Bound Method
A bound method object is a thin, dynamic C struct that holds exactly two pointers:
1. `__self__`: A pointer to the instance (`light`), acting as the **Receiver**.
2. `__func__`: A pointer to the underlying function object (`Light.turn_on`), acting as the **Concrete Action**.

When you invoke `cmd()`, the C interpreter intercepts the call, pushes `__self__` as the first argument onto the stack, and executes `__func__`.

### Architectural Conclusion
The bound method object cleanly encapsulates the Receiver and the Action, and it provides a unified `__call__` interface for the Invoker. **Python generates Concrete Commands dynamically at runtime for free**, entirely eliminating the need for boilerplate Command classes.
