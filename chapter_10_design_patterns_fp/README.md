# Chapter 10 — Design Patterns with First-Class Functions

> **Theme**: Many classic Gang of Four (GoF) design patterns are unnecessarily complex in Python. Because functions are first-class objects, we can replace heavyweight Abstract Base Classes with simple `Callable` references.

## What You'll Learn

| Topic | Key insight |
|-------|------------|
| Peter Norvig's Insight | In 1996, Norvig proved that 16 of the 23 GoF patterns are invisible or simpler in languages with first-class functions. |
| The Strategy Pattern | Replace abstract Strategy classes with simple functions. |
| The Command Pattern | Replace Invoker interfaces with callables or closures. |
| The Template Method | Pass functions to algorithms instead of forcing class inheritance. |
| The "Java-in-Python" Anti-pattern | Writing classes with exactly one method (besides `__init__`) is usually a mistake in Python. |

## Key Files

- [`examples.py`](examples.py) — Side-by-side refactoring of OOP Strategy/Command to FP.
- [`exercises.py`](exercises.py) — Refactoring the Template Method and building a Command Queue.
- [`mini_project.py`](mini_project.py) — E-commerce checkout applying Strategy (promotions) and Command (event hooks).
- [`benchmarks.py`](benchmarks.py) — Proves that passing function references is ~2x faster than instantiating Strategy objects.
- [`notes.md`](notes.md) — Theory on pattern simplification.
- [`pitfalls.md`](pitfalls.md) — When *not* to use functions (i.e., when state gets too complex).
- [`interview_questions.md`](interview_questions.md) — L3 to L6 interview prep.
- [`architecture_notes.md`](architecture_notes.md) — CPython's bounded methods as implicit Command objects.

## 30-Second Rules

```python
# Rule 1: Replace single-method classes with functions
# BAD:
class Discount(ABC):
    @abstractmethod
    def apply(self, price): pass
class VIPDiscount(Discount):
    def apply(self, price): return price * 0.8

# GOOD:
def vip_discount(price): return price * 0.8

# Rule 2: Use lists of Callables for MacroCommands
hooks = [send_email, update_db, clear_cache]
for hook in hooks: hook()
```

*Reference: Fluent Python 2nd ed., Chapter 10 — pages 381–402*
