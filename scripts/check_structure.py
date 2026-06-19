#!/usr/bin/env python3
"""
check_structure.py — Validate that all chapter folders are complete.

Checks each chapter_XX_* directory for the required files.
Reports missing files and gives a completion summary.

Usage:
    python scripts/check_structure.py
    python scripts/check_structure.py --strict  # Exit with error if incomplete
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_FILES = [
    "README.md",
    "examples.py",
    "exercises.py",
    "mini_project.py",
    "benchmarks.py",
    "notes.md",
    "pitfalls.md",
    "interview_questions.md",
    "architecture_notes.md",
]

STUB_MARKERS = ["Coming soon", "Coming Soon", "Placeholder", "TODO: implement"]


def is_stub(filepath: Path) -> bool:
    """Check if a file is a stub (contains placeholder content)."""
    try:
        content = filepath.read_text(encoding="utf-8")
        return any(marker in content for marker in STUB_MARKERS)
    except Exception:
        return False


def check_chapter(chapter_dir: Path) -> dict:
    """Check a single chapter directory. Returns result dict."""
    result = {
        "name": chapter_dir.name,
        "present": [],
        "missing": [],
        "stubs": [],
        "complete": False,
    }

    for filename in REQUIRED_FILES:
        filepath = chapter_dir / filename
        if filepath.exists():
            result["present"].append(filename)
            if is_stub(filepath):
                result["stubs"].append(filename)
        else:
            result["missing"].append(filename)

    result["complete"] = len(result["missing"]) == 0 and len(result["stubs"]) == 0
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate fluent-python-journey chapter structure."
    )
    parser.add_argument("--strict", action="store_true", help="Exit with error if any chapter is incomplete")
    parser.add_argument("--base", type=Path, default=Path(__file__).parent.parent)
    args = parser.parse_args()

    base_dir = args.base
    chapter_dirs = sorted(
        [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("chapter_")]
    )

    if not chapter_dirs:
        print("❌ No chapter directories found.")
        sys.exit(1)

    print("=" * 65)
    print("  Fluent Python Journey — Structure Check")
    print("=" * 65)
    print(f"  Base: {base_dir}")
    print(f"  Chapters found: {len(chapter_dirs)}")
    print()

    total_complete = 0
    total_incomplete = 0
    all_missing: list[str] = []

    for chapter_dir in chapter_dirs:
        result = check_chapter(chapter_dir)

        if result["complete"]:
            status = "✅"
            total_complete += 1
        elif result["missing"]:
            status = "❌"
            total_incomplete += 1
        else:
            status = "⚠️ "
            total_incomplete += 1

        stub_info = f"  ({len(result['stubs'])} stubs)" if result["stubs"] else ""
        missing_info = f"  MISSING: {result['missing']}" if result["missing"] else ""

        print(f"  {status} {result['name']}{stub_info}{missing_info}")
        all_missing.extend(result["missing"])

    print()
    print("─" * 65)
    print(f"  Complete:   {total_complete}/{len(chapter_dirs)} chapters")
    print(f"  Incomplete: {total_incomplete}/{len(chapter_dirs)} chapters")

    if total_incomplete == 0:
        print("\n  🎉 All chapters are complete and fully implemented!")
    else:
        print(f"\n  💡 Next: complete the ⚠️/❌ chapters above.")

    print()

    if args.strict and total_incomplete > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
