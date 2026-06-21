# Chapter 10: Design Patterns with First-Class Functions — Notes

## 1. The Core Premise
In 1996, Peter Norvig noted that 16 out of the 23 design patterns in the original *Design Patterns* book (Gamma et al.) are "invisible or simpler" in languages with first-class functions (like Lisp, or Python). 
Python's ability to treat functions as objects makes many heavyweight OOP patterns redundant.

## 2. The Strategy Pattern
**The Goal:** Define a family of algorithms, encapsulate each one, and make them interchangeable.

**Classic OOP implementation:**
1. Context object `Order` holds a reference to a Strategy interface.
2. Abstract Base Class `PromotionStrategy` defines a `.discount()` method.
3. Concrete subclasses `VIPPromotion`, `BulkPromotion` implement `.discount()`.

**Pythonic implementation:**
1. A strategy is just a `Callable` passed as a parameter.
2. No Abstract Base Classes. No single-method subclasses.
3. You just pass `vip_promo_function` directly to the `Order`.

*Benefits:* Less boilerplate. Functions are lighter than class instances.

## 3. The Command Pattern
**The Goal:** Decouple the object that invokes an operation from the one that knows how to perform it.

**Classic OOP implementation:**
An `Invoker` holds an instance of an `AbstractCommand` and calls its `.execute()` method.

**Pythonic implementation:**
An `Invoker` holds a `Callable` and calls `func()`. If the command requires state (arguments to be executed later), you can use `functools.partial` or a closure to freeze the arguments, entirely bypassing the need for a custom class with an `__init__` and `execute()` method.

## 4. The MacroCommand
If you need to execute a sequence of commands, you don't need a complex Composite pattern. A `MacroCommand` in Python can simply be a class that stores a list of `Callable` objects and implements `__call__` to iterate through them.

## 5. Identifying the "Java-in-Python" Anti-pattern
If you find yourself writing a class with:
1. An `__init__` method.
2. Exactly one other method (like `execute`, `run`, or `apply`).

...you are likely writing Java in Python. That class should almost certainly be a simple function or a closure.
