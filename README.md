# 📖 Fluent Python Journey

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Book](https://img.shields.io/badge/Book-Fluent%20Python%202nd%20Ed-FF6B35?style=for-the-badge)
![Progress](https://img.shields.io/badge/Progress-2%2F24%20Chapters-4CAF50?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Code Style](https://img.shields.io/badge/code%20style-ruff%20%2B%20black-000000?style=for-the-badge)

**A chapter-by-chapter deep engineering journey through Fluent Python (2nd Ed.) by Luciano Ramalho.**  
Not a tutorial copy — an original exploration of Python's internals, design, and performance.

[📚 Chapters](#-chapter-index) · [⚡ Benchmarks](#-performance-highlights) · [🧠 Learning Journal](LEARNING_JOURNAL.md) · [🤝 Contributing](CONTRIBUTING.md)

</div>

---

## 🎯 Goals

This repository is not a study summary. It is an **engineering portfolio** built in public.

Every chapter produces:
- **Original implementations** — reinterpreting book concepts, not copying them
- **Benchmarks** — measuring real performance with `timeit`, `tracemalloc`, `perf_counter`
- **Architecture analysis** — asking *why* Python is designed this way
- **Interview-grade explanations** — articulating concepts under pressure
- **Mini-projects** — applying concepts to real-world scenarios

The target audience is someone who wants to understand Python at a **senior engineer level** — not just write code that works, but understand *why* it works and *when* to use what.

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

| # | Chapter | Status | Key Concepts | Benchmark |
|---|---------|--------|-------------|-----------|
| 01 | [The Python Data Model](chapter_01_python_data_model/) | ✅ Complete | `__dunder__`, protocols, special methods | Dunder vs explicit calls |
| 02 | [An Array of Sequences](chapter_02_sequences/) | 🔄 Active | listcomp, memoryview, slicing, deque | List vs tuple vs array memory |
| 03 | [Dicts and Sets](chapter_03_dicts_sets/) | 📋 Planned | hash tables, dict internals, set ops | Dict lookup vs list scan |
| 04 | [Unicode Text vs Bytes](chapter_04_unicode_text_bytes/) | 📋 Planned | encoding, codec, binary protocols | — |
| 05 | [Data Class Builders](chapter_05_data_class_builders/) | 📋 Planned | dataclasses, NamedTuple, attrs | — |
| 06 | [Object References](chapter_06_object_references/) | 📋 Planned | identity, equality, copy, weakref | Shallow vs deep copy |
| 07 | [Functions as First Class](chapter_07_functions_first_class/) | 📋 Planned | closures, HOF, functools | — |
| 08 | [Type Hints in Functions](chapter_08_type_hints_functions/) | 📋 Planned | annotations, mypy, Protocol | — |
| 09 | [Decorators and Closures](chapter_09_decorators_closures/) | 📋 Planned | `@wraps`, parametrized decorators | Decorator overhead |
| 10 | [Design Patterns with FP](chapter_10_design_patterns_fp/) | 📋 Planned | Strategy, Command via functions | — |

> **Legend**: ✅ Complete · 🔄 Active · 📋 Planned

---

## ⚡ Performance Highlights

Key benchmark findings documented across chapters:

| Benchmark | Finding | Chapter |
|-----------|---------|---------|
| `len(obj)` vs `obj.__len__()` | Dunder dispatch via `len()` is ~15% faster due to C-level shortcut | Ch. 01 |
| `list` vs `tuple` memory | Tuple uses ~30% less memory for same data; list over-allocates | Ch. 02 |
| List comprehension vs `map()` | Listcomp is 10–25% faster for simple transforms; `map` shines for large iterables | Ch. 02 |
| `memoryview` slicing | Zero-copy slicing is **100x faster** for large binary data vs regular slice | Ch. 02 |
| `array.array` vs `list` | `array` uses 4x less memory for numeric data | Ch. 02 |

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
- **Write idiomatic Python** — code that senior engineers recognize as well-crafted

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
