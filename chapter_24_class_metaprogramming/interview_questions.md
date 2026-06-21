# Chapter 24 — Interview Questions: Class Metaprogramming

---

## 🟢 L3

### Q1: What is the difference between an Object and a Class in Python?
An Object is an instance of a Class. A Class is an instance of a Metaclass. Everything in Python is an object, including classes themselves. The default metaclass that builds all classes in Python is `type`.

---

## 🟡 L4

### Q2: What is the difference between Evaluation Time and Execution Time?
Evaluation Time (Import Time) occurs when Python first reads the module from top to bottom. It executes all top-level statements, including compiling the body of all `class` definitions.
Execution Time (Runtime) occurs when functions or methods are actually called.
Metaprogramming (like Class Decorators and Metaclasses) runs exclusively at Evaluation Time. If your metaprogramming has a bug, your app will crash before `main()` is even called.

---

## 🔴 L5

### Q3: Why did Python 3.6 introduce `__init_subclass__` when Metaclasses already existed?
Metaclasses are notoriously difficult to write, and more importantly, they cause the "Metaclass Conflict" bug. If you inherit from two parent classes that use different metaclasses, Python crashes with a `TypeError`.
`__init_subclass__` allows a parent class to hook into the creation of any subclass *without* using a Metaclass. It solves 90% of metaprogramming use cases (like auto-registering plugins or validating attributes) in a completely safe, inheritance-friendly way.

---

## 🟣 L6

### Q4: Explain the signature and purpose of `metaclass.__new__`.
The signature is `def __new__(meta_cls, cls_name, bases, cls_dict)`.
This method is called *before* the class physically exists in memory.
*   `meta_cls`: The metaclass itself.
*   `cls_name`: The string name of the class being built (e.g., "UserModel").
*   `bases`: A tuple of the parent classes.
*   `cls_dict`: A dictionary containing all the methods and variables defined inside the class body.

By intercepting `cls_dict`, you can dynamically inject new functions, delete variables, or validate data before passing the modified dictionary to `super().__new__` to actually compile the class into memory.
