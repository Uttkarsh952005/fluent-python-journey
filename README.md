# 📖 Fluent Python Journey

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Book](https://img.shields.io/badge/Book-Fluent%20Python%202nd%20Ed-FF6B35?style=for-the-badge)
![Progress](https://img.shields.io/badge/Progress-24%2F24%20Chapters-4CAF50?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Code Style](https://img.shields.io/badge/code%20style-ruff%20%2B%20black-000000?style=for-the-badge)

**A chapter-by-chapter deep engineering journey through Fluent Python (2nd Ed.) by Luciano Ramalho.**  
Not a tutorial copy — an original exploration of Python's internals, design, and performance.

[📚 Chapters](#-chapter-index) · [⚡ Benchmarks](#-performance-highlights) · [🧠 Learning Journal](LEARNING_JOURNAL.md) · [🤝 Contributing](CONTRIBUTING.md)

</div>

---

## 🎯 Goals

This repository is a **structured engineering notebook** built in public.

Every chapter produces:
- **Original implementations** — reinterpreting book concepts, not copying them
- **Benchmarks** — measuring real performance with `timeit`, `tracemalloc`, `perf_counter`
- **Architecture analysis** — asking *why* Python is designed this way
- **Interview-grade explanations** — articulating concepts under pressure
- **Mini-projects** — applying concepts to real-world scenarios

The target audience is someone who wants to understand Python at a **systems-oriented level** — not just write code that works, but understand *why* it works and *when* to use what.

---

## 🏗️ Repository Architecture

```
fluent-python-journey/
│
├── chapter_XX_<topic>/
│   ├── README.md              # Deep concept breakdown with diagrams
│   ├── examples.py            # Annotated, runnable original implementations
│   ├── exercises.py           # Original exercises extending book concepts
│   ├── mini_project.py        # Standalone project applying chapter concepts
│   ├── benchmarks.py          # Performance measurements with analysis
│   ├── notes.md               # Structured learning notes
│   ├── pitfalls.md            # Common mistakes + production fixes
│   ├── interview_questions.md # Senior-level Q&A
│   └── architecture_notes.md  # Design decisions and Python internals
│
├── scripts/
│   ├── scaffold_chapter.py    # Auto-generate new chapter structure
│   ├── check_structure.py     # Validate all chapters are complete
│   └── generate_commit_plan.py # Generate realistic commit message plan
│
├── LEARNING_JOURNAL.md        # Weekly reflections and insights
├── CONTRIBUTING.md            # How to navigate and contribute
├── requirements.txt           # Project dependencies
└── pyproject.toml             # Ruff, mypy, black configuration
```

---

## 📚 Chapter Index

| # | Chapter | Status | Key Concepts |
|---|---------|--------|-------------|
| 01 | [The Python Data Model](chapter_01_python_data_model/) | ✅ Complete | `__dunder__`, protocols, special methods |
| 02 | [An Array of Sequences](chapter_02_sequences/) | ✅ Complete | listcomp, memoryview, slicing, deque, bisect |
| 03 | [Dicts and Sets](chapter_03_dicts_sets/) | ✅ Complete | hash tables, dict internals, `|` merge, set ops |
| 04 | [Unicode Text vs Bytes](chapter_04_unicode_text_bytes/) | ✅ Complete | encoding, codec, NFC/NFD, Unicode sandwich |
| 05 | [Data Class Builders](chapter_05_data_class_builders/) | ✅ Complete | `namedtuple`, `NamedTuple`, `@dataclass`, `field()` |
| 06 | [Object References](chapter_06_object_references/) | ✅ Complete | identity, equality, shallow/deep copy, `del`, GC |
| 07 | [Functions as First Class](chapter_07_functions_first_class/) | ✅ Complete | closures, HOF, `functools`, `operator` |
| 08 | [Type Hints in Functions](chapter_08_type_hints_functions/) | ✅ Complete | annotations, mypy, Protocol |
| 09 | [Decorators and Closures](chapter_09_decorators_closures/) | ✅ Complete | `@wraps`, parametrized decorators |
| 10 | [Design Patterns with FP](chapter_10_design_patterns_fp/) | ✅ Complete | Strategy, Command via functions |
| 11 | [A Pythonic Object](chapter_11_pythonic_object/) | ✅ Complete | `__repr__`, `__str__`, `__format__`, `__slots__` |
| 12 | [Special Methods for Sequences](chapter_12_sequences_special_methods/) | ✅ Complete | vector class, slicing, dynamic attributes |
| 13 | [Interfaces, Protocols, and ABCs](chapter_13_interfaces_protocols_abcs/) | ✅ Complete | duck typing, goose typing, `abc` module |
| 14 | [Inheritance: For Better or For Worse](chapter_14_inheritance/) | ✅ Complete | `super()`, multiple inheritance, MRO |
| 15 | [More About Type Hints](chapter_15_more_type_hints/) | ✅ Complete | overloaded, TypedDict, cast |
| 16 | [Operator Overloading](chapter_16_operator_overloading/) | ✅ Complete | infix operators, augmented assignment |
| 17 | [Iterators, Generators, and Classic Coroutines](chapter_17_iterators_generators/) | ✅ Complete | `yield`, `yield from`, `itertools` |
| 18 | [with, match, and else Blocks](chapter_18_with_match_else/) | ✅ Complete | context managers, pattern matching |
| 19 | [Concurrency Models in Python](chapter_19_concurrency_models/) | ✅ Complete | processes, threads, GIL, asyncio vs multiprocessing |
| 20 | [Concurrent Executors](chapter_20_concurrent_executors/) | ✅ Complete | `concurrent.futures`, ThreadPoolExecutor |
| 21 | [Asynchronous Programming](chapter_21_asyncio/) | ✅ Complete | `async def`, `await`, event loop |
| 22 | [Dynamic Attributes and Properties](chapter_22_dynamic_attributes/) | ✅ Complete | `__getattr__`, `@property`, JSON parsing |
| 23 | [Attribute Descriptors](chapter_23_attribute_descriptors/) | ✅ Complete | `__get__`, `__set__`, property internals |
| 24 | [Class Metaprogramming](chapter_24_class_metaprogramming/) | ✅ Complete | class decorators, `__new__`, `type`, metaclasses |

> **Legend**: ✅ Complete · 📋 Planned

---

## ⚡ Performance Highlights

| Benchmark | Finding | Chapter |
|-----------|---------|---------| 
| `len(obj)` vs `obj.__len__()` | Dunder dispatch via `len()` is ~15% faster (C shortcut) | Ch. 01 |
| `list` vs `tuple` memory | Tuple uses ~30% less memory; list over-allocates | Ch. 02 |
| `memoryview` slicing | Zero-copy slicing is **100x faster** for large binary data | Ch. 02 |
| Dict lookup vs list scan | Dict O(1) vs list O(n) — 50x faster at N=10,000 | Ch. 03 |
| `namedtuple` vs `@dataclass` memory | namedtuple uses ~3x less memory (no `__dict__`) | Ch. 05 |
| `is` vs `==` | `is` is ~2-3x faster — single integer compare, no `__eq__` | Ch. 06 |
| `copy` vs `deepcopy` | deepcopy is 10-100x slower depending on nesting depth | Ch. 06 |

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/Uttkarsh952005/fluent-python-journey.git
cd fluent-python-journey

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run Chapter 1 benchmarks
python chapter_01_python_data_model/benchmarks.py

# Run Chapter 2 benchmarks
python chapter_02_sequences/benchmarks.py

# Validate repository structure
python scripts/check_structure.py
```

---

## 📊 Learning Outcomes

By working through this repository alongside the book, you will:

- **Understand Python's object model** — why everything is an object, how protocols work
- **Read CPython source patterns** — why `len()` calls `sq_length` in C, not `__len__` directly
- **Measure and reason about performance** — know *when* to optimize, not just *how*
- **Think architecturally** — choose the right data structure for the right problem
- **Write practical Python** — code that is structured, efficient, and well-crafted

---

## 🔗 Related Repositories

| Repo | Purpose |
|------|---------|
| [python-internals-playground](https://github.com/Uttkarsh952005/python-internals-playground) | Deep dives into dunder methods, descriptors, metaclasses |
| [python-performance-lab](https://github.com/Uttkarsh952005/python-performance-lab) | Systematic benchmarking of Python data structures and algorithms |
| [python-visualized](https://github.com/Uttkarsh952005/python-visualized) | Visual explanations of Python internals with matplotlib |
| [python-design-patterns-pythonic](https://github.com/Uttkarsh952005/python-design-patterns-pythonic) | Pythonic design patterns with UML diagrams |
| [python-concurrency-lab](https://github.com/Uttkarsh952005/python-concurrency-lab) | Async, threading, and multiprocessing projects |
| [python-pitfalls-and-tricks](https://github.com/Uttkarsh952005/python-pitfalls-and-tricks) | Advanced Python mistakes, fixes, and interview traps |

---

## 📖 References

- **Fluent Python, 2nd Edition** — Luciano Ramalho (O'Reilly, 2022)
- [CPython Source Code](https://github.com/python/cpython)
- [Python Data Model Documentation](https://docs.python.org/3/reference/datamodel.html)
- [PEP 3107 — Function Annotations](https://peps.python.org/pep-3107/)
- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

<div align="center">

*Built in public. Learning in depth. Engineering with intention.*

**[Uttkarsh](https://github.com/Uttkarsh952005)** · Python Engineer in Progress

</div>
