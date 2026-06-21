"""
Chapter 10: Exercises — Design Patterns with First-Class Functions
==================================================================
Original exercises applying functional refactoring to classic patterns.
"""

import sys
from typing import Callable

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: Refactor Template Method
# ─────────────────────────────────────────────────────────────────────────────
# The Template Method pattern defines the skeleton of an algorithm in a base class,
# letting subclasses override specific steps.
# Refactor this class-based approach into a single function that accepts Callables 
# for the specific steps.

# THE OLD WAY:
class ReportGenerator:
    def generate(self) -> str:
        data = self.fetch_data()
        return self.format_data(data)
    def fetch_data(self) -> str: raise NotImplementedError
    def format_data(self, data: str) -> str: raise NotImplementedError

# TODO: Write a purely functional `generate_report`
def generate_report(fetcher: Callable[[], str], formatter: Callable[[str], str]) -> str:
    # Implement the template structure here
    return formatter(fetcher())

def test_ex1_template() -> None:
    section("Exercise 1: Functional Template Method")
    
    def get_db_data() -> str: return "raw_db_row"
    def html_format(d: str) -> str: return f"<b>{d}</b>"
    
    res = generate_report(get_db_data, html_format)
    print(f"Generated report: {res}")
    assert res == "<b>raw_db_row</b>", "Exercise 1 failed"
    print("✓ Exercise 1 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Building a Command Queue
# ─────────────────────────────────────────────────────────────────────────────
# Implement a `CommandQueue` class. It should accept Callables.
# It has an `add_task(func)` method and a `run_all()` method.
# If a function fails, the queue should catch the error, print it, and continue.

class CommandQueue:
    def __init__(self):
        # TODO: Initialize tasks list
        self.tasks: list[Callable] = []
        
    def add_task(self, task: Callable) -> None:
        # TODO: Add to list
        self.tasks.append(task)
        
    def run_all(self) -> int:
        """Runs all tasks and returns the number of successful tasks."""
        # TODO: Implement robust execution loop
        success_count = 0
        for task in self.tasks:
            try:
                task()
                success_count += 1
            except Exception as e:
                print(f"Task failed: {e}")
        return success_count

def test_ex2_command_queue() -> None:
    section("Exercise 2: Command Queue")
    
    queue = CommandQueue()
    queue.add_task(lambda: print("Task 1 Done"))
    queue.add_task(lambda: 1 / 0)  # Will fail
    queue.add_task(lambda: print("Task 3 Done"))
    
    successes = queue.run_all()
    print(f"Successful tasks: {successes}")
    assert successes == 2, "Exercise 2 failed"
    print("✓ Exercise 2 passed")


if __name__ == "__main__":
    test_ex1_template()
    test_ex2_command_queue()
