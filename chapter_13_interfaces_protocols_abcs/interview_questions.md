# Chapter 13 — Interview Questions: Interfaces and Protocols

---

## 🟢 L3

### Q1: What is "Duck Typing"?
Duck Typing is a dynamic typing approach where the type or the class of an object is less important than the methods it defines. When you use duck typing, you do not check types at all. You just invoke the method (`obj.speak()`) and assume it will work. If the method is missing, Python raises an `AttributeError` at runtime.

---

### Q2: What is an Abstract Base Class (ABC)?
An ABC is a class that cannot be instantiated directly. It exists solely to define an interface for subclasses. Subclasses must override methods marked with `@abstractmethod`. If they fail to do so, they also become abstract and cannot be instantiated.

---

## 🟡 L4

### Q3: When should you use `isinstance(obj, abc.Sequence)` instead of duck typing?
You use explicit `isinstance` checks against ABCs ("Goose Typing") when you are building a framework or boundary layer that needs to **fail fast**. Duck typing fails deeply inside your code when the missing method is finally called. Goose typing fails immediately at the boundary if the passed object isn't structurally valid.

---

### Q4: Explain the difference between `NotImplemented` and `NotImplementedError`.
`NotImplementedError` is an exception you `raise` inside an abstract method to indicate that subclasses must implement it.
`NotImplemented` is a special singleton value you `return` from dunder operator methods (like `__add__` or `__eq__`) to tell Python that your class doesn't know how to handle the operation, allowing Python to try the reverse operation on the other operand.

---

## 🔴 L5

### Q5: What is a "Virtual Subclass" in Python?
A virtual subclass is a class that is registered to an ABC using the `register()` method (e.g., `Sequence.register(MyCustomList)`). Once registered, `isinstance(MyCustomList(), Sequence)` will return `True`, even though `MyCustomList` does not inherit from `Sequence`. It is a way to declare compatibility without modifying the class's inheritance tree. Crucially, virtual subclasses do not inherit any actual code or mixin methods from the ABC.

---

## 🟣 L6

### Q6: What is the exact difference between `abc.ABC` and `typing.Protocol`? How do they fundamentally differ in CPython's execution?
`abc.ABC` is an artifact of the runtime. When you subclass an ABC, the metaclass `ABCMeta` runs at class creation time, maintaining a registry of abstract methods and physically preventing instantiation of the class at runtime if any are missing.
`typing.Protocol` is a static construct introduced in PEP 544. A standard protocol is completely ignored at runtime by CPython. It exists purely for static type checkers (like Mypy) to verify that an object structurally matches the expected interface during the CI/CD pipeline, achieving type safety without the tight coupling of inheritance.
