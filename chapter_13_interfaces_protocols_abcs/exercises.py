"""
Chapter 13: Exercises — Monkey Patching and Virtual Subclasses
==============================================================
Original exercises demonstrating how to alter classes at runtime to fulfill 
protocols, and how to register classes to ABCs without subclassing them.
"""

import sys
import collections.abc

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: Monkey Patching a Protocol
# ─────────────────────────────────────────────────────────────────────────────
# random.shuffle() requires a MutableSequence. It needs __len__, __getitem__,
# and crucially, __setitem__. 
# Here we have a class that is missing __setitem__. We will monkey-patch it 
# at runtime to make it compatible with shuffle().

import random

class Deck:
    def __init__(self):
        self._cards = ['Ace', 'King', 'Queen', 'Jack']
        
    def __len__(self): return len(self._cards)
    def __getitem__(self, position): return self._cards[position]
    # BUG: Missing __setitem__, so random.shuffle(Deck()) will fail!

def set_card(deck, position, card):
    """Function to be monkey-patched into the Deck class."""
    deck._cards[position] = card

def test_ex1_monkey_patching() -> None:
    section("Exercise 1: Monkey Patching")
    d = Deck()
    
    try:
        random.shuffle(d)
        assert False, "Should have failed!"
    except TypeError as e:
        print(f"Failed to shuffle: {e}")
        
    # TODO: Monkey patch the Deck class
    print("Monkey patching Deck.__setitem__...")
    Deck.__setitem__ = set_card
    
    # Now it works!
    random.shuffle(d)
    print(f"Shuffled deck: {list(d)}")
    print("✓ Exercise 1 passed")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Virtual Subclassing
# ─────────────────────────────────────────────────────────────────────────────
# ABCs have a `.register()` method. You can tell Python "Trust me, this class 
# implements the ABC, even though it doesn't inherit from it."

class RegisteredSequence:
    """Doesn't inherit from anything!"""
    pass

def test_ex2_virtual_subclass() -> None:
    section("Exercise 2: Virtual Subclassing")
    
    obj = RegisteredSequence()
    print(f"Is it a sequence naturally? {isinstance(obj, collections.abc.Sequence)}")
    
    # TODO: Register the class as a virtual subclass of Sequence
    collections.abc.Sequence.register(RegisteredSequence)
    
    print(f"Is it a sequence after registration? {isinstance(obj, collections.abc.Sequence)}")
    assert isinstance(obj, collections.abc.Sequence)
    print("✓ Exercise 2 passed")


if __name__ == "__main__":
    test_ex1_monkey_patching()
    test_ex2_virtual_subclass()
