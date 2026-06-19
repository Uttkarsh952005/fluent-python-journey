#!/usr/bin/env python3
"""
generate_commit_plan.py — Generate a realistic commit history plan for a chapter.

Outputs ordered, meaningful commit messages that simulate natural engineering progress.
Use this to plan your commit sequence before starting a chapter.

Usage:
    python scripts/generate_commit_plan.py 02 "An Array of Sequences"
"""

from __future__ import annotations

import argparse
import datetime


COMMIT_TEMPLATES = [
    # Initial setup
    ("feat", "{chapter_tag}", "initialize chapter structure and README skeleton"),
    ("docs", "{chapter_tag}", "add chapter overview and key questions to README"),

    # Notes first (research phase)
    ("docs", "{chapter_tag}", "add structured notes on {concept_1}"),
    ("docs", "{chapter_tag}", "document {concept_2} internals in notes.md"),

    # Examples (implementation phase)
    ("feat", "{chapter_tag}", "implement {concept_1} examples with annotations"),
    ("feat", "{chapter_tag}", "add {concept_2} demo with edge cases"),
    ("feat", "{chapter_tag}", "implement {concept_3} examples"),

    # Benchmarks
    ("bench", "{chapter_tag}", "benchmark {concept_1} vs {concept_2} performance"),
    ("bench", "{chapter_tag}", "add memory profiling for {concept_1}"),
    ("bench", "{chapter_tag}", "document benchmark findings in README"),

    # Exercises
    ("feat", "{chapter_tag}", "add exercise 1: {exercise_1}"),
    ("feat", "{chapter_tag}", "add exercise 2: {exercise_2}"),
    ("feat", "{chapter_tag}", "add exercise 3: {exercise_3}"),

    # Mini project
    ("feat", "{chapter_tag}", "implement mini-project: {mini_project}"),
    ("feat", "{chapter_tag}", "add error handling and edge cases to mini-project"),
    ("docs", "{chapter_tag}", "document mini-project architecture decisions"),

    # Pitfalls and interview
    ("docs", "{chapter_tag}", "document common pitfalls for {concept_1}"),
    ("docs", "{chapter_tag}", "add interview questions L3-L5"),
    ("docs", "{chapter_tag}", "add L6 staff-level interview question with CPython internals"),

    # Architecture
    ("docs", "{chapter_tag}", "write architecture notes on Python design decisions"),

    # Polish
    ("refactor", "{chapter_tag}", "improve annotations and type hints in examples.py"),
    ("docs", "{chapter_tag}", "update root README progress tracker"),
    ("chore", "{chapter_tag}", "add chapter to LEARNING_JOURNAL.md with reflections"),
]


def generate_plan(chapter_num: str, title: str) -> None:
    chapter_tag = f"ch{chapter_num}"
    chapter_folder = f"chapter_{chapter_num}_{title.lower().replace(' ', '_')[:25]}"

    print("=" * 70)
    print(f"  Commit Plan: Chapter {chapter_num} — {title}")
    print("=" * 70)
    print(f"  Branch suggestion: feature/chapter-{chapter_num}")
    print(f"  Folder: {chapter_folder}/")
    print()

    # Generate realistic dates (spread over ~5 days)
    start_date = datetime.date.today()
    commits_per_day = [4, 5, 4, 4, 6]  # spread across 5 days
    commit_idx = 0

    for day_offset, daily_count in enumerate(commits_per_day):
        date = start_date + datetime.timedelta(days=day_offset)
        print(f"  📅 Day {day_offset + 1} ({date.strftime('%Y-%m-%d')}):")

        for _ in range(daily_count):
            if commit_idx >= len(COMMIT_TEMPLATES):
                break
            prefix, tag, msg = COMMIT_TEMPLATES[commit_idx]
            full_tag = tag.format(chapter_tag=chapter_tag)
            formatted = msg.format(
                chapter_tag=chapter_tag,
                concept_1="[fill: first concept]",
                concept_2="[fill: second concept]",
                concept_3="[fill: third concept]",
                exercise_1="[fill: exercise name]",
                exercise_2="[fill: exercise name]",
                exercise_3="[fill: exercise name]",
                mini_project="[fill: project name]",
            )
            print(f"    git commit -m '{prefix}({full_tag}): {formatted}'")
            commit_idx += 1

        print()

    print("  💡 Customize the [fill: ...] placeholders with chapter-specific terms.")
    print("  💡 Add commits between these as your implementation grows.")
    print("  💡 Never: 'update file', 'fix stuff', 'wip', or whitespace commits.")
    print()
    print("  Example actual commits for Chapter 2:")
    print("    feat(ch02): implement array.array memory demo with sys.getsizeof")
    print("    bench(ch02): benchmark memoryview slice vs bytearray copy — 100x faster")
    print("    feat(ch02): add RingBuffer exercise using deque(maxlen)")
    print("    docs(ch02): document list growth policy with CPython formula")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a realistic commit plan for a chapter."
    )
    parser.add_argument("number", help="Chapter number (e.g., 02)")
    parser.add_argument("title", help="Chapter title")
    args = parser.parse_args()
    generate_plan(args.number, args.title)


if __name__ == "__main__":
    main()
