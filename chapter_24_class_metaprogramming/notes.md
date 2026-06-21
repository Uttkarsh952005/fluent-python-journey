# Chapter 24: Class Metaprogramming — Notes

## 1. What is a Metaclass?
Just as an object is an instance of a Class, a Class is an instance of a Metaclass.
If you type `type(7)`, it returns `<class 'int'>`.
If you type `type(int)`, it returns `<class 'type'>`.
`type` is the default metaclass that Python uses to build all classes. A custom metaclass is simply a class that inherits from `type` and overrides `__new__` or `__init__` to intercept the class-creation process.

## 2. Evaluation Time vs Execution Time
*   **Evaluation Time (Import Time):** When Python first imports a module, it reads it top-to-bottom. It executes all top-level code. Crucially, it executes the *body* of every class definition, builds the class dictionary, and calls the Metaclass/Class Decorators to construct the Class Object in memory.
*   **Execution Time (Runtime):** This happens when the user actually invokes things. Calling `obj = MyClass()` triggers `__init__`. Calling `obj.do_work()` triggers the method. Metaprogramming logic almost exclusively runs at Evaluation Time.

## 3. The Three Tiers of Metaprogramming
1.  **Class Decorators (`@decorator`):** Evaluated *after* the class is fully built. Great for attaching new attributes or wrapping the class.
2.  **`__init_subclass__`:** A modern (Python 3.6+) feature. Placed in a parent class, it is automatically triggered whenever a subclass is defined. It is the perfect, safe replacement for Metaclasses for 90% of use cases (like automatic plugin registries).
3.  **Metaclasses:** Evaluated *during* class creation. They can physically intercept the raw `dict` of variables and methods before the class object even exists in memory. This is the nuclear option. Use only for massive framework architecture (like Django ORM).
