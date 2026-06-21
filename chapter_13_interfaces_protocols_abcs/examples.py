"""
Chapter 13: Interfaces, Protocols, and ABCs
===========================================
Original implementations exploring the three pillars of Python interfaces:
Dynamic Duck Typing, Runtime Goose Typing (ABCs), and Static Duck Typing (Protocols).

Key concepts covered:
- Duck Typing (Implicit, runtime)
- Goose Typing (Explicit subclassing of abc.ABC)
- Static Duck Typing (typing.Protocol for static checkers)
- Custom Abstract Base Classes (ABCs)
"""

import sys
import abc
import random
from typing import Protocol, runtime_checkable

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Dynamic Duck Typing
# ─────────────────────────────────────────────────────────────────────────────
# Python doesn't care what the object *is*, only what it can *do*.
# We don't inherit from anything.

class DuckVocalizer:
    def speak(self): return "Quack!"

class DogVocalizer:
    def speak(self): return "Woof!"

def duck_type_demo(entity) -> None:
    # We just assume 'speak' exists. If it doesn't, it crashes at runtime.
    print(f"Duck typing says: {entity.speak()}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Static Duck Typing (PEP 544 Protocols)
# ─────────────────────────────────────────────────────────────────────────────
# Protocols allow STATIC type checkers (Mypy) to verify structural subtyping 
# without requiring the class to inherit from anything.

@runtime_checkable
class SupportsSpeak(Protocol):
    def speak(self) -> str: ...

# Robot doesn't inherit from SupportsSpeak! But it matches the structure.
class Robot:
    def speak(self) -> str: return "Beep boop."

def protocol_demo(entity: SupportsSpeak) -> None:
    # Mypy statically verifies 'entity' has a speak() returning str.
    print(f"Static Duck (Protocol) says: {entity.speak()}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Goose Typing (Abstract Base Classes)
# ─────────────────────────────────────────────────────────────────────────────
# Goose typing requires explicit inheritance from an ABC, guaranteeing 
# the interface at instantiation time rather than call time.

class Tombola(abc.ABC):
    """An abstract base class for a random item dispenser."""
    
    @abc.abstractmethod
    def load(self, iterable):
        """Add items from an iterable."""
        
    @abc.abstractmethod
    def pick(self):
        """Remove item at random, returning it."""
        
    def loaded(self) -> bool:
        """Concrete mixin method relying on abstract methods."""
        return bool(self.inspect())
        
    def inspect(self) -> tuple:
        """Concrete mixin returning a sorted tuple of items."""
        items = []
        while True:
            try:
                items.append(self.pick())
            except LookupError:
                break
        self.load(items)
        return tuple(sorted(items))


class BingoCage(Tombola):
    """Concrete implementation of the Tombola ABC."""
    def __init__(self, items):
        self._randomizer = random.SystemRandom()
        self._items = []
        self.load(items)

    def load(self, items):
        self._items.extend(items)
        self._randomizer.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError("pick from empty BingoCage")


def goose_type_demo() -> None:
    cage = BingoCage([10, 20, 30])
    print(f"BingoCage loaded? {cage.loaded()}")
    print(f"Inspecting contents: {cage.inspect()}")
    print(f"Picked: {cage.pick()}")
    
    # ABCs prevent instantiation of incomplete classes
    class FakeTombola(Tombola):
        def load(self, iterable): pass
        # Forgot to implement pick()!
        
    try:
        FakeTombola()
    except TypeError as e:
        print(f"ABC blocked instantiation: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    section("1. Dynamic Duck Typing")
    duck_type_demo(DuckVocalizer())
    duck_type_demo(DogVocalizer())

    section("2. Static Duck Typing (Protocols)")
    protocol_demo(Robot())
    # Since we used @runtime_checkable, we can do this at runtime:
    print(f"Is Robot a SupportsSpeak? {isinstance(Robot(), SupportsSpeak)}")

    section("3. Goose Typing (ABCs)")
    goose_type_demo()
