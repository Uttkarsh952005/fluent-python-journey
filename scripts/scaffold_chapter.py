#!/usr/bin/env python3
"""
scaffold_chapter.py — Auto-generate a new chapter folder with all required files.

Usage:
    python scripts/scaffold_chapter.py 11 "Special Methods for Sequences"

This creates:
    chapter_11_special_methods_for_sequences/
    ├── README.md
    ├── examples.py
    ├── exercises.py
    ├── mini_project.py
    ├── benchmarks.py
    ├── notes.md
    ├── pitfalls.md
    ├── interview_questions.md
    └── architecture_notes.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Templates
# ─────────────────────────────────────────────────────────────────────────────

README_TEMPLATE = """\
# Chapter {num} — {title}

<div align="center">

![Status](https://img.shields.io/badge/Status-In%20Progress-FF9800?style=flat-square)

</div>

> *"Quote from the book here."*
> — Luciano Ramalho, Fluent Python

---

## 🧠 What This Chapter Is Really About

[Your insight here — what's the deeper lesson beyond the surface examples?]

---

## 📐 Core Concepts

### 1. [Concept One]
[Explanation]

### 2. [Concept Two]
[Explanation]

---

## 📊 Performance Summary

| Operation | Notes |
|-----------|-------|
| [benchmark] | [result] |

---

## 📁 Files in This Chapter

| File | Description |
|------|-------------|
| [`examples.py`](examples.py) | Original implementations |
| [`exercises.py`](exercises.py) | Progressive exercises |
| [`mini_project.py`](mini_project.py) | Standalone mini project |
| [`benchmarks.py`](benchmarks.py) | Performance measurements |
| [`notes.md`](notes.md) | Structured reference notes |
| [`pitfalls.md`](pitfalls.md) | Common mistakes + fixes |
| [`interview_questions.md`](interview_questions.md) | Senior-level Q&A |
| [`architecture_notes.md`](architecture_notes.md) | Design decisions |
"""

EXAMPLES_TEMPLATE = """\
\"\"\"
Chapter {num}: {title} — Examples
{'=' * (len(title) + 20)}
Original implementations demonstrating chapter concepts.

Key concepts:
- [concept 1]
- [concept 2]
- [concept 3]

Run with: python examples.py
\"\"\"

from __future__ import annotations


def demo_concept_one() -> None:
    \"\"\"Demonstrate [concept one].\"\"\"
    pass  # TODO: implement


def demo_concept_two() -> None:
    \"\"\"Demonstrate [concept two].\"\"\"
    pass  # TODO: implement


if __name__ == "__main__":
    demo_concept_one()
    demo_concept_two()
"""

EXERCISES_TEMPLATE = """\
\"\"\"
Chapter {num}: Exercises — {title}
{'=' * (len(title) + 15)}
Progressive exercises to deepen understanding.
\"\"\"

from __future__ import annotations


# =============================================================================
# Exercise 1: [Title]
# =============================================================================
# Description of what to build.


class Exercise1:
    pass  # TODO: implement


# =============================================================================
# Demo
# =============================================================================

def run_exercises() -> None:
    print("=== Exercise 1 ===")
    # TODO: test your implementation


if __name__ == "__main__":
    run_exercises()
"""

MINI_PROJECT_TEMPLATE = """\
\"\"\"
Chapter {num}: Mini Project — [Project Name]
{'=' * 40}
Description of what this project demonstrates.

Concepts demonstrated:
- [concept 1]
- [concept 2]

Run with: python mini_project.py
\"\"\"

from __future__ import annotations


def main() -> None:
    print("Chapter {num} Mini Project")
    # TODO: implement


if __name__ == "__main__":
    main()
"""

BENCHMARKS_TEMPLATE = """\
\"\"\"
Chapter {num}: Benchmarks — {title}
{'=' * (len(title) + 15)}
Performance measurements for chapter concepts.

Run with: python benchmarks.py
\"\"\"

from __future__ import annotations

import timeit


NUMBER = 100_000


def bench(label: str, stmt: str, setup: str = "pass") -> float:
    t = timeit.timeit(stmt=stmt, setup=setup, number=NUMBER, globals=globals())
    ns = (t / NUMBER) * 1e9
    print(f"  {{label:<50}} {{ns:>8.1f}} ns/op")
    return ns


def main() -> None:
    print("=== Chapter {num} Benchmarks ===\\n")

    # TODO: Add benchmarks
    bench("placeholder", "1 + 1")


if __name__ == "__main__":
    main()
"""

NOTES_TEMPLATE = """\
# Chapter {num} — Notes: {title}

## Core Concept

[Explain the main idea in your own words]

## Key Methods / Functions

| Name | Purpose |
|------|---------|
| [method] | [what it does] |

## Vocabulary

| Term | Definition |
|------|-----------|
| [term] | [definition] |
"""

PITFALLS_TEMPLATE = """\
# Chapter {num} — Pitfalls: {title}

## Pitfall 1: [Name]

### The Mistake
```python
# Broken code here
```

### Why It Happens
[Explanation]

### The Fix
```python
# Correct code here
```

---

## Interview Relevance

- [Question this pitfall maps to]
"""

INTERVIEW_TEMPLATE = """\
# Chapter {num} — Interview Questions: {title}

> Questions from L3 (junior) to L6 (staff engineer) level.

---

## 🟢 L3 — Junior

### Q1: [Question]

**Expected answer:**
[Answer with depth appropriate for a senior Python engineer]

---

## 🟡 L4 — Mid-Level

### Q2: [Question]

**Expected answer:**
[Answer]

---

## 🔴 L5 — Senior

### Q3: [Question]

**Expected answer:**
[Answer with CPython internals and design rationale]
"""

ARCHITECTURE_TEMPLATE = """\
# Chapter {num} — Architecture Notes: {title}

## Key Design Decision: [Title]

### The Decision
[What Python chose to do]

### The Trade-offs

| Aspect | Python's Choice | Alternative |
|--------|----------------|-------------|
| [aspect] | [choice] | [alternative] |

### Why This Matters
[Practical implications for engineers]
"""


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def slugify(title: str) -> str:
    """Convert title to folder-safe slug."""
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def scaffold(chapter_num: int, title: str, base_dir: Path) -> None:
    folder_name = f"chapter_{chapter_num:02d}_{slugify(title)}"
    chapter_dir = base_dir / folder_name

    if chapter_dir.exists():
        print(f"❌ Chapter directory already exists: {chapter_dir}")
        sys.exit(1)

    chapter_dir.mkdir(parents=True)
    print(f"📁 Created: {chapter_dir}")

    ctx = {"num": f"{chapter_num:02d}", "title": title}

    files = [
        ("README.md", README_TEMPLATE.format(**ctx)),
        ("examples.py", EXAMPLES_TEMPLATE.format(**ctx)),
        ("exercises.py", EXERCISES_TEMPLATE.format(**ctx)),
        ("mini_project.py", MINI_PROJECT_TEMPLATE.format(**ctx)),
        ("benchmarks.py", BENCHMARKS_TEMPLATE.format(**ctx)),
        ("notes.md", NOTES_TEMPLATE.format(**ctx)),
        ("pitfalls.md", PITFALLS_TEMPLATE.format(**ctx)),
        ("interview_questions.md", INTERVIEW_TEMPLATE.format(**ctx)),
        ("architecture_notes.md", ARCHITECTURE_TEMPLATE.format(**ctx)),
    ]

    for filename, content in files:
        filepath = chapter_dir / filename
        filepath.write_text(content, encoding="utf-8")
        print(f"  ✅ {filename}")

    print(f"\n✨ Chapter {chapter_num:02d} scaffold complete: {folder_name}/")
    print(f"   Next steps:")
    print(f"   1. Fill in README.md with concepts and diagrams")
    print(f"   2. Build examples.py with original implementations")
    print(f"   3. Run benchmarks.py to get real numbers")
    print(f"   4. Update root README.md progress tracker")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a new Fluent Python chapter folder with all required files."
    )
    parser.add_argument("number", type=int, help="Chapter number (e.g., 11)")
    parser.add_argument("title", type=str, help="Chapter title (e.g., 'Special Methods for Sequences')")
    parser.add_argument(
        "--base",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Base directory (default: repo root)",
    )

    args = parser.parse_args()
    scaffold(args.number, args.title, args.base)


if __name__ == "__main__":
    main()
