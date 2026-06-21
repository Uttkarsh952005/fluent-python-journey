# Chapter 10 — Interview Questions: Design Patterns with First-Class Functions

---

## 🟢 L3

### Q1: What is the primary difference between how Java and Python implement the Strategy pattern?
In older versions of Java, you must define an interface (or abstract base class) and create separate concrete classes that implement that interface. In Python, because functions are first-class objects, a Strategy is simply a function passed as an argument. There is no need for abstract base classes or single-method concrete classes.

---

### Q2: What is the "Java-in-Python" anti-pattern?
It's the tendency of developers from rigid OOP backgrounds to write unnecessarily complex class hierarchies in Python. The most common symptom is writing a class that has an `__init__` method and exactly one other method (like `execute()` or `run()`), instead of just writing a simple function.

---

## 🟡 L4

### Q3: How do you implement the Command pattern functionally in Python?
The Command pattern aims to decouple the invoker of an action from the object that performs the action. In Python, you can achieve this by simply passing a `Callable` (a function or method reference) to the invoker. If the command requires arguments that are not available at invocation time, you can use a closure or `functools.partial` to "freeze" those arguments into a parameter-less callable.

---

### Q4: If you use functions instead of classes for the Strategy pattern, how do you enforce that the functions have the correct signature?
By using `typing.Callable` in your type hints. For example, if the strategy expects an `Order` object and returns a `float`, you annotate the parameter as `strategy: Callable[[Order], float]`. Static analysis tools like Mypy will then enforce the "interface" just as strictly as an Abstract Base Class would.

---

## 🔴 L5

### Q5: What was Peter Norvig's 1996 thesis regarding the "Gang of Four" design patterns?
Norvig presented a famous slide deck showing that 16 of the 23 design patterns from the classic *Design Patterns* book are either "invisible or simpler" in languages with first-class functions, macros, and dynamic typing (he used Lisp/Dylan, but it applies perfectly to Python). The thesis is that many GoF patterns are actually workarounds for flaws or missing features in C++ and Java.

---

### Q6: When *shouldn't* you refactor a single-method class into a function?
You should stick to a class if the operation requires managing complex, mutable state over time. While you *can* manage state using closures and the `nonlocal` keyword, doing so for highly complex state makes the code unreadable. Classes are the optimal tool for coupling state with behavior.

---

## 🟣 L6

### Q7: Explain how a bound method in CPython is an implicit implementation of the Command pattern.
In CPython, when you access a method on an instance (e.g., `obj.do_something`), you get a bound method object (`types.MethodType`). This object acts as a lightweight Command. It encapsulates both the function to be executed (`__func__`) and the receiver of the action (`__self__`, which is the instance). You can pass this bound method around and execute it later with zero arguments, perfectly fulfilling the Command pattern's requirements without writing any custom wrapper classes.
