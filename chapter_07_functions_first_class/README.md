# Chapter 7 — Functions as First-Class Objects

> **Theme**: Functions in Python are real, tangible objects. They can be created, assigned, passed, returned, and inspected just like an integer or a dictionary.

## What You'll Learn

| Topic | Key insight |
|-------|------------|
| First-Class Functions | Functions are objects of the `function` class. |
| Higher-Order Functions | Functions that take or return other functions (`map`, `filter`, `sorted`). |
| `__call__` method | Any object can act like a function if it implements `__call__`. |
| `lambda` functions | Restricted to a single pure expression. Often abused. |
| Modern Replacements | List comprehensions are usually faster/clearer than `map`/`filter`. |
| Parameter Signatures | `/` for positional-only, `*` for keyword-only arguments. |
| Functional Primitives | `operator` module and `functools.partial` replace trivial lambdas. |

## Key Files

- [`examples.py`](examples.py) — Core implementations of signatures, `__call__`, and `operator`.
- [`exercises.py`](exercises.py) — 5 original exercises including Fredrik Lundh's lambda refactoring.
- [`mini_project.py`](mini_project.py) — Functional pluggable rule engine for password validation.
- [`benchmarks.py`](benchmarks.py) — Performance: `itemgetter` vs `lambda`, listcomp vs `map`.
- [`notes.md`](notes.md) — Reference tables for callables and parameters.
- [`pitfalls.md`](pitfalls.md) — Production traps: map consumption, lambda loop binding.
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — CPython's `PyFunctionObject` and `METH_FASTCALL`.

## 30-Second Rules

```python
# Rule 1: Use comprehensions over map/filter
bad = list(map(upper, filter(is_even, data)))
good = [upper(x) for x in data if is_even(x)]

# Rule 2: Use operator module over trivial lambdas
bad = sorted(data, key=lambda x: x[1])
good = sorted(data, key=itemgetter(1))

# Rule 3: Use functools.partial to adapt signatures
bad = button.on_click(lambda: do_action("save"))
good = button.on_click(partial(do_action, "save"))
```

*Reference: Fluent Python 2nd ed., Chapter 7 — pages 231–252*
