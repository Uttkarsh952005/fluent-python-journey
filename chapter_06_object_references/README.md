# Chapter 6 — Object References, Mutability, and Recycling

> **Theme**: Names are labels stuck to objects — not boxes containing them. This single mental model explains aliasing, mutability bugs, copy semantics, and garbage collection.

## What You'll Learn

| Topic | Key insight |
|-------|------------|
| Variables as labels | Assignment binds a name to an object, not a copy |
| `is` vs `==` | Identity vs value — use `==` for almost everything |
| Tuple immutability | Tuples can't change their references, but referents can mutate |
| Shallow copy | New outer container, shared inner objects |
| Deep copy | Full independent duplicate, handles cycles |
| Call-by-sharing | Parameters are aliases of arguments |
| Mutable defaults | Defaults evaluated once — shared across all calls |
| `del` and GC | `del` removes a name; CPython uses reference counting |

## Key Files

- [`examples.py`](examples.py) — 6-part walkthrough of all book examples
- [`exercises.py`](exercises.py) — 5 exercises with verification
- [`mini_project.py`](mini_project.py) — Document graph inspector (aliasing, deepcopy, weakref)
- [`benchmarks.py`](benchmarks.py) — `is` vs `==`, `copy` vs `deepcopy` speed
- [`notes.md`](notes.md) — Quick reference tables
- [`pitfalls.md`](pitfalls.md) — 7 production bugs
- [`interview_questions.md`](interview_questions.md) — 9 questions L3→L6
- [`architecture_notes.md`](architecture_notes.md) — CPython refcount & GC internals

## 30-Second Rules

```
y = x              → alias (same object)
y = list(x)        → shallow copy (new outer, shared inners)
y = copy.deepcopy(x) → deep copy (everything new)

x is None          → correct (singleton check)
x == "hello"       → correct (value check)
x is "hello"       → WRONG (interning is an implementation detail)

def f(items=[]):   → BUG (mutable default shared)
def f(items=None): → CORRECT (create fresh list inside)
  items = list(items) if items else []
```

*Reference: Fluent Python 2nd ed., Chapter 6 — pages 201–223*
