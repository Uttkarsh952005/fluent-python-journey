"""
Chapter 1: The Python Data Model
=================================
Original implementations exploring Python's special method protocol.

Key concepts demonstrated:
- __repr__, __str__, __len__, __getitem__, __contains__
- __bool__, __abs__, __add__, __mul__
- How protocols enable duck typing
- The difference between calling len() vs .__len__()

NOT a copy of the book — these are original extensions exploring the same concepts.
"""

from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")


import collections
import math
import random
from typing import Iterator


# =============================================================================
# PART 1: Extending the FrenchDeck Concept
# =============================================================================

# The book shows a simple FrenchDeck. Here we build a more complete Card system
# that demonstrates how implementing just __len__ and __getitem__ unlocks the
# entire Python sequence ecosystem.

Card = collections.namedtuple("Card", ["rank", "suit"])

SUIT_SYMBOLS = {
    "spades": "♠",
    "hearts": "♥",
    "diamonds": "♦",
    "clubs": "♣",
}

SUIT_VALUES = {"spades": 3, "hearts": 2, "diamonds": 1, "clubs": 0}

RANK_VALUES = {
    rank: value
    for value, rank in enumerate(
        ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"],
        start=2,
    )
}


class FrenchDeck:
    """
    A standard 52-card French deck implemented using only __len__ and __getitem__.

    By implementing these two methods, we gain for FREE:
    - len(deck)             → __len__
    - deck[0], deck[-1]     → __getitem__
    - deck[0:5]             → __getitem__ with slice
    - for card in deck      → __getitem__ with sequential integer keys
    - 'card in deck'        → sequential __getitem__ scan (no __contains__ needed)
    - random.choice(deck)   → uses len() and __getitem__ internally
    - random.shuffle(deck)  → needs __setitem__ too (shown below in MutableDeck)
    - sorted(deck, ...)     → uses __getitem__ iteration
    - reversed(deck)        → uses __len__ and __getitem__

    This is the power of Python's data model: one small surface area unlocks
    a massive ecosystem of functionality.
    """

    RANKS = [str(n) for n in range(2, 11)] + list("JQKA")
    SUITS = ["clubs", "diamonds", "hearts", "spades"]

    def __init__(self) -> None:
        self._cards: list[Card] = [
            Card(rank, suit) for suit in self.SUITS for rank in self.RANKS
        ]

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, position: int | slice) -> Card | list[Card]:
        return self._cards[position]

    def __repr__(self) -> str:
        top = self._cards[0]
        bottom = self._cards[-1]
        return (
            f"FrenchDeck({len(self)} cards, "
            f"top={top.rank}{SUIT_SYMBOLS[top.suit]}, "
            f"bottom={bottom.rank}{SUIT_SYMBOLS[bottom.suit]})"
        )

    def __contains__(self, card: object) -> bool:
        """
        Override the default __contains__ (sequential scan) with O(1) lookup.
        Without this, 'card in deck' iterates through all cards.
        With this, it's instant.

        LESSON: Python falls back to __getitem__ iteration for 'in', but
        you should provide __contains__ when you can do better than O(n).
        """
        return isinstance(card, Card) and card in set(self._cards)


def spades_high_key(card: Card) -> int:
    """Sort key: higher rank = higher value; spades beat others at same rank."""
    return RANK_VALUES[card.rank] * 4 + SUIT_VALUES[card.suit]


# =============================================================================
# PART 2: Vector2D — Numeric Protocol
# =============================================================================


class Vector2D:
    """
    A 2D vector implementing the numeric special method protocol.

    Demonstrates:
    - __repr__ (developer-facing) vs __str__ (user-facing)
    - __abs__ for magnitude
    - __bool__ for truthiness (zero vector is falsy)
    - __add__ and __mul__ for arithmetic
    - __eq__ for equality
    - __hash__ (must implement when __eq__ is defined)
    - __iter__ for unpacking: x, y = vector

    Design decision: we make Vector2D immutable (no __setattr__ override)
    so it's hashable and safe to use as dict key.
    """

    __slots__ = ("_x", "_y")  # memory optimization: no __dict__

    def __init__(self, x: float, y: float) -> None:
        self._x = float(x)
        self._y = float(y)

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def __repr__(self) -> str:
        """Developer representation: unambiguous, reconstructable."""
        return f"Vector2D({self._x!r}, {self._y!r})"

    def __str__(self) -> str:
        """User representation: readable coordinates."""
        return f"({self._x}, {self._y})"

    def __abs__(self) -> float:
        """Magnitude of the vector using the Pythagorean theorem."""
        return math.hypot(self._x, self._y)

    def __bool__(self) -> bool:
        """
        A zero vector (0, 0) is falsy; any non-zero vector is truthy.

        LESSON: __bool__ should return bool, not int. While Python accepts
        any integer return, being explicit avoids subtle bugs.

        Alternative: return bool(abs(self)) — but this is less efficient
        for a zero-check. Direct comparison is O(1) vs computing hypot.
        """
        return bool(self._x or self._y)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector2D):
            return (self._x, self._y) == (other._x, other._y)
        return NotImplemented  # Let Python try the other side

    def __hash__(self) -> int:
        """
        Must define __hash__ when defining __eq__.
        Python removes __hash__ from classes that define __eq__ without __hash__,
        making them unhashable (can't be used as dict keys or in sets).
        """
        return hash((self._x, self._y))

    def __add__(self, other: Vector2D) -> Vector2D:
        """Vector addition: component-wise."""
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self._x + other._x, self._y + other._y)

    def __mul__(self, scalar: float) -> Vector2D:
        """Scalar multiplication: Vector2D * number."""
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self._x * scalar, self._y * scalar)

    def __rmul__(self, scalar: float) -> Vector2D:
        """
        Reflected multiplication: number * Vector2D.

        Without __rmul__, `2 * Vector2D(1, 2)` raises TypeError because
        int.__mul__ doesn't know about Vector2D and returns NotImplemented.
        Python then tries the right operand's __rmul__ — that's this method.
        """
        return self.__mul__(scalar)

    def __iter__(self) -> Iterator[float]:
        """
        Makes the vector unpackable: x, y = Vector2D(3, 4)
        Also enables: list(vector), tuple(vector)

        LESSON: __iter__ is the primary protocol. If absent, Python falls
        back to __getitem__ with integer indices starting at 0.
        """
        yield self._x
        yield self._y

    def dot(self, other: Vector2D) -> float:
        """Dot product: not a dunder but a domain method."""
        return self._x * other._x + self._y * other._y


# =============================================================================
# PART 3: Protocol Demonstration — What You Get For Free
# =============================================================================


class RangeSet:
    """
    A lazy integer range that behaves like a set using only:
    - __len__ for cardinality
    - __contains__ for membership (O(1) math check)
    - __iter__ for iteration

    This demonstrates how you can implement a minimal protocol surface
    and still get rich behavior from the standard library.
    """

    def __init__(self, start: int, stop: int) -> None:
        self.start = start
        self.stop = stop

    def __len__(self) -> int:
        return max(0, self.stop - self.start)

    def __contains__(self, item: object) -> bool:
        """O(1) membership test — no iteration needed."""
        return isinstance(item, int) and self.start <= item < self.stop

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.start, self.stop))

    def __repr__(self) -> str:
        return f"RangeSet({self.start}, {self.stop})"


# =============================================================================
# DEMO FUNCTIONS
# =============================================================================


def demo_french_deck() -> None:
    """Show how __len__ + __getitem__ unlocks the ecosystem."""
    deck = FrenchDeck()
    print("=== FrenchDeck Demo ===")
    print(f"repr: {deck!r}")
    print(f"len: {len(deck)}")
    print(f"First card: {deck[0]}")
    print(f"Last card: {deck[-1]}")
    print(f"Top 3: {deck[:3]}")
    print(f"Random card: {random.choice(deck)}")
    print(f"Ace of spades in deck: {Card('A', 'spades') in deck}")

    print("\nTop 5 cards by rank (spades-high sort):")
    for card in sorted(deck, key=spades_high_key)[-5:]:
        print(f"  {card.rank}{SUIT_SYMBOLS[card.suit]}")


def demo_vector2d() -> None:
    """Show the numeric protocol in action."""
    v1 = Vector2D(3, 4)
    v2 = Vector2D(1, 2)

    print("\n=== Vector2D Demo ===")
    print(f"repr(v1): {v1!r}")
    print(f"str(v1): {v1}")
    print(f"abs(v1): {abs(v1)}")
    print(f"bool(v1): {bool(v1)}")
    print(f"bool(Vector2D(0,0)): {bool(Vector2D(0, 0))}")
    print(f"v1 + v2: {v1 + v2!r}")
    print(f"v1 * 3: {v1 * 3!r}")
    print(f"3 * v1: {3 * v1!r}")

    x, y = v1  # Works because of __iter__
    print(f"Unpacking: x={x}, y={y}")

    vectors = {v1, v2, Vector2D(3, 4)}  # Works because of __hash__
    print(f"In a set (v1 and Vector2D(3,4) are same): {len(vectors)} unique vectors")


def demo_range_set() -> None:
    """Show minimal protocol surface with rich behavior."""
    rs = RangeSet(1, 101)
    print("\n=== RangeSet Demo ===")
    print(f"repr: {rs!r}")
    print(f"len: {len(rs)}")
    print(f"42 in rs: {42 in rs}")
    print(f"150 in rs: {150 in rs}")
    print(f"sum(rs): {sum(rs)}")  # Works via __iter__
    print(f"list(rs)[:5]: {list(rs)[:5]}")  # Works via __iter__


if __name__ == "__main__":
    demo_french_deck()
    demo_vector2d()
    demo_range_set()
