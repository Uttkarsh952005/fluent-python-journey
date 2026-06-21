# Chapter 23 — Interview Questions: Attribute Descriptors

---

## 🟢 L3

### Q1: What is the primary use case for an Attribute Descriptor?
Descriptors are used to abstract away `@property` getter and setter logic into a reusable class. If you have 10 different attributes that all need to be validated as "positive integers", writing 10 `@property` methods violates DRY (Don't Repeat Yourself). You can write a single `PositiveInteger` descriptor class and instantiate it 10 times at the class level.

---

## 🟡 L4

### Q2: Why is it dangerous for a descriptor to store data on `self`?
A descriptor is instantiated as a Class Attribute, not an Instance Attribute. Therefore, there is only one instance of the descriptor class shared globally among all instances of the managed class. If you store data on `self` (e.g., `self.value = 5`), you overwrite that value for every single object in your application simultaneously. Data must always be stored in `instance.__dict__`.

---

## 🔴 L5

### Q3: What is the architectural difference between an Overriding and Non-Overriding Descriptor?
An Overriding Descriptor implements `__set__`. Because Python checks overriding descriptors *before* checking the instance dictionary during an attribute lookup, they completely intercept assignments (`obj.attr = 5`). The user cannot overwrite them.
A Non-Overriding Descriptor only implements `__get__`. Because Python checks the instance dictionary *before* checking non-overriding descriptors, typing `obj.attr = 5` will bypass the descriptor and create a raw variable `obj.__dict__['attr'] = 5`, permanently shadowing the descriptor.

---

## 🟣 L6

### Q4: How are Python methods implemented under the hood?
Python functions are actually Non-Overriding Descriptors! Every function object in Python has a `__get__` method.
When you access a function via an instance (`obj.my_method`), the `__get__` method of the function is invoked. The function's `__get__` method dynamically returns a **Bound Method** object, which acts as a wrapper that automatically injects the `instance` as the first argument (`self`) when the function is finally called. This is the entire mechanism behind Python's object-oriented method binding!
