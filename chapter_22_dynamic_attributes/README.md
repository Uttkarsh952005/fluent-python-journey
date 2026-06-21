# Chapter 22 — Dynamic Attributes and Properties

> **Theme**: Python allows you to dynamically intercept attribute lookups. This enables the creation of elegant, declarative APIs (like Django ORM or Pydantic) by transforming dictionary keys into dot-notation object attributes.

## What You'll Learn

| Concept | Explanation |
|---------|------------|
| `__getattr__` | Intercepts attribute lookups ONLY when the attribute does not exist. |
| `__getattribute__` | Intercepts EVERY attribute lookup unconditionally. Highly dangerous. |
| `@property` | Allows you to execute a function when a user accesses a basic attribute, enforcing the Uniform Access Principle. |
| `__new__` | The true object constructor. Executes before `__init__` and physically returns the instance. |

## Key Files

- [`examples.py`](examples.py) — Building a recursive JSON wrapper (`FrozenJSON`) from scratch using `__getattr__`.
- [`exercises.py`](exercises.py) — The infamous `__getattr__` infinite recursion loop, and why you must sanitize Python keywords (like `class`) in APIs.
- [`mini_project.py`](mini_project.py) — A robust API client wrapper that overrides `__new__` to dynamically return either a list or a parsed object depending on the raw JSON type.
- [`benchmarks.py`](benchmarks.py) — Proves that metaprogramming adds a 2x–3x CPU overhead compared to accessing raw dictionary keys.
- [`notes.md`](notes.md) — The mechanical difference between `__getattr__` and `__getattribute__`.
- [`pitfalls.md`](pitfalls.md) — The severe architectural mistake of hiding heavy I/O operations (like database queries) behind simple `@property` lookups.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — How `functools.cached_property` hacks the CPython `__dict__` sequence to achieve O(1) performance.

## 30-Second Rules

```python
# Rule 1: Always use __getattr__, NEVER use __getattribute__ unless you are an expert.
# __getattribute__ requires `super().__getattribute__(name)` to avoid infinite loops.

# Rule 2: If a JSON response contains a Python keyword, append an underscore.
if keyword.iskeyword(key):
    key += '_'  # 'class' becomes 'class_'

# Rule 3: Use @functools.cached_property for expensive dynamically calculated attributes.
@cached_property
def query_results(self):
    return run_large_db_query() # Only runs on the very first access!
```

*Reference: Fluent Python 2nd ed., Chapter 22 — pages 863–905*
