# Chapter 24 — Pitfalls: Class Metaprogramming

---

## Pitfall 1: The Metaclass Conflict

In Python, a class can inherit from multiple parent classes. But what happens if Parent A was built by `MetaA`, and Parent B was built by `MetaB`?

```python
class MetaA(type): pass
class MetaB(type): pass

class ClassA(metaclass=MetaA): pass
class ClassB(metaclass=MetaB): pass

# FATAL CRASH: TypeError: metaclass conflict: the metaclass of a derived class 
# must be a (non-strict) subclass of the metaclasses of all its bases
class Child(ClassA, ClassB): 
    pass
```

**Why it fails:** Python does not know which metaclass should be responsible for building `Child`. 
**Fix:** You must create a new metaclass that inherits from both `MetaA` and `MetaB`, and assign it to `Child`. Because this is a nightmare to maintain, you should almost always use `__init_subclass__` instead of Metaclasses.

---

## Pitfall 2: I/O during Evaluation Time

Because metaprogramming executes at **Evaluation Time** (Import Time), placing blocking operations inside a metaclass is disastrous.

```python
class DatabaseMeta(type):
    def __new__(meta, name, bases, dic):
        # BUG: This runs when the file is IMPORTED.
        # If the DB is down, `import my_models` will hard crash the app 
        # before `main()` or the web server can even start up and catch the error!
        ping_database() 
        return super().__new__(meta, name, bases, dic)
```

**Fix:** Keep Evaluation Time strictly for structural processing (validating strings, parsing schemas, injecting functions). Delay all I/O, network requests, and database calls to Execution Time (Runtime).

---

## Pitfall 3: Tim Peters' Golden Rule of Metaclasses

*“Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don't (the people who actually need them know with certainty that they need them, and don't need an explanation about why).”* — Tim Peters (Author of the Zen of Python).
