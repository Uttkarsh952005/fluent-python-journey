"""
Chapter 17: Iterators, Generators, and Classic Coroutines
=========================================================
Original implementations exploring lazy evaluation, the 'yield' 
suspension mechanic, generator delegation via 'yield from', 
and classic coroutines using '.send()'.
"""

import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Lazy Generators (yield)
# ─────────────────────────────────────────────────────────────────────────────
# Instead of building a massive list in memory, we yield one item at a time.
# This makes processing massive datasets O(1) in memory.

WORD_RE = re.compile(r'\w+')

class LazySentence:
    def __init__(self, text):
        self.text = text

    def __iter__(self):
        """This method is a generator function because it contains 'yield'."""
        # Finditer evaluates lazily. It doesn't build a list of all matches.
        for match in WORD_RE.finditer(self.text):
            yield match.group()

def demo_lazy_generator() -> None:
    section("Part 1: Lazy Generators")
    s = LazySentence("Generators suspend their state and return control to the caller.")
    
    # We iterate over the generator. It yields one word, pauses, and resumes.
    for word in s:
        print(f"  Yielded: {word}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Generator Delegation (yield from)
# ─────────────────────────────────────────────────────────────────────────────
# 'yield from' links a caller directly to an inner generator, bypassing the 
# outer generator loop entirely.

def sub_generator():
    yield "Sub-Gen 1"
    yield "Sub-Gen 2"

def delegating_generator():
    yield "Outer start"
    # Instead of `for x in sub_generator(): yield x`
    yield from sub_generator()
    yield "Outer end"

def demo_yield_from() -> None:
    section("Part 2: 'yield from' Delegation")
    for item in delegating_generator():
        print(f"  {item}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Classic Coroutines (.send())
# ─────────────────────────────────────────────────────────────────────────────
# A generator becomes a coroutine when you send data INTO it using .send() 
# instead of just pulling data out of it using next().

def moving_average_coroutine():
    """A coroutine that computes a running average."""
    total = 0.0
    count = 0
    average = None
    
    while True:
        # Execution SUSPENDS here. It waits for `.send(term)`
        term = yield average
        
        # If term is None, the coroutine can handle it or exit
        if term is None:
            break
            
        total += term
        count += 1
        average = total / count

def demo_coroutine() -> None:
    section("Part 3: Classic Coroutines (.send)")
    coro = moving_average_coroutine()
    
    # PRIMING: We MUST call next(coro) or coro.send(None) first to 
    # advance execution to the very first `yield` statement.
    next(coro)
    
    # Now we send data INTO the suspended generator
    print(f"  Sent 10, average: {coro.send(10)}")
    print(f"  Sent 20, average: {coro.send(20)}")
    print(f"  Sent 30, average: {coro.send(30)}")
    
    coro.close() # Cleanly shuts down the coroutine


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_lazy_generator()
    demo_yield_from()
    demo_coroutine()
