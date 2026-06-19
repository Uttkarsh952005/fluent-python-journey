# Chapter 3 — Dicts and Sets

<div align="center">

![Status](https://img.shields.io/badge/Status-Planned-9E9E9E?style=flat-square)
![Concepts](https://img.shields.io/badge/Concepts-Hash%20Tables%20%7C%20Dict%20Internals%20%7C%20Set%20Operations-FF6B35?style=flat-square)

</div>

> *"The dict type is not only widely used in our programs, but also a key part of the Python implementation."*
> — Luciano Ramalho, Fluent Python

---

## 🧠 Key Questions to Answer

1. How does Python's hash table work internally? What's the load factor?
2. Why did dict ordering change in Python 3.7? Was it guaranteed before?
3. When should you use `defaultdict` vs `Counter` vs `ChainMap`?
4. Why are sets faster than lists for membership tests? What's the time complexity?
5. How do hash collisions affect dict performance?
6. What is `__hash__` contract and why does it matter for dict correctness?

---

## 📋 Planned Content

### Core Topics
- `dict` internal structure: compact dict (Python 3.6+), hash table probing
- Dict views (`keys()`, `values()`, `items()`) — set-like operations
- `defaultdict`, `OrderedDict`, `ChainMap`, `Counter` — when to use which
- Set operations: union, intersection, difference, symmetric difference
- Frozenset — immutable, hashable, usable as dict key
- Dict comprehensions and set comprehensions
- Merging dicts: `|` operator (Python 3.9+), `update()`, `**unpacking`

### Performance Deep Dive
- Dict lookup: O(1) average, O(n) worst case (hash collisions)
- Set vs list for membership test: O(1) vs O(n)
- Memory layout: why dicts are compact since Python 3.6
- Hash table load factor and rehashing

---

## 📁 Planned Files

| File | Status |
|------|--------|
| `README.md` | ✅ This file |
| `examples.py` | 📋 Planned |
| `exercises.py` | 📋 Planned |
| `mini_project.py` | 📋 Planned — Word frequency analysis engine |
| `benchmarks.py` | 📋 Planned — Dict lookup vs list scan |
| `notes.md` | 📋 Planned |
| `pitfalls.md` | 📋 Planned |
| `interview_questions.md` | 📋 Planned |
| `architecture_notes.md` | 📋 Planned |

---

*Coming after Chapter 2 is fully documented and benchmarked.*
