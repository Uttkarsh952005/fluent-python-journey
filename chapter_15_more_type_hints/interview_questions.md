# Chapter 15 — Interview Questions: Advanced Type Hints

---

## 🟢 L3

### Q1: What is the difference between `Any` and `object` in type hinting?
`Any` completely disables the type checker. It tells Mypy "trust me, anything goes here." You can call `.foo()` on `Any` and Mypy won't complain.
`object` is the root of the class hierarchy. Every class in Python inherits from `object`. It is strictly typed. If you type a variable as `object`, Mypy will only let you call methods that exist on `object` itself (like `__str__` or `__eq__`). Calling `.foo()` on `object` will raise a static type error.

---

## 🟡 L4

### Q2: What is a `TypedDict` and when should you use it over a `dataclass`?
A `TypedDict` allows you to declare the schema (expected keys and value types) for a standard Python dictionary.
You should use it when you are dealing with raw JSON payloads coming from an API or database, where the data is fundamentally structured as a dict and you want to maintain zero runtime overhead (avoiding the CPU cost of instantiating real `dataclass` objects).

---

## 🔴 L5

### Q3: How do you use `@typing.overload`?
You use `@overload` to define multiple type signatures for a single function without implementing the logic. 
You stack several `@overload` definitions with empty bodies (`...` or `pass`). Finally, you provide one concrete implementation *without* the decorator. This concrete implementation must have a signature broad enough to handle all the overloaded cases (often using `Union` or `Any`). Mypy uses the overloaded signatures for checking, while Python only executes the concrete logic.

### Q4: Is `typing.cast(TargetType, my_obj)` safe to use for data validation?
Absolutely not. `cast` does exactly zero runtime validation. If you do `cast(int, "hello")`, Python just returns the string `"hello"`. It is simply a directive that tells the static type checker to blindly trust that the variable is of `TargetType`. If you need actual validation, you must use a library like `pydantic` or write manual `isinstance` checks.

---

## 🟣 L6

### Q5: What is a "Generic Type" (`TypeVar`) and how does it affect variance?
A `TypeVar` allows you to parameterize classes and functions so that the type checker understands relationships between inputs and outputs (e.g., `def first(l: List[T]) -> T:`). 
By default, custom generics are **invariant** (Mypy will reject a `List[SubClass]` if it expects `List[BaseClass]`). You can make them **covariant** (`TypeVar('T', covariant=True)`) if the container is read-only, meaning Mypy will accept `List[SubClass]` safely because nothing will be written to the container that might violate the base type.
