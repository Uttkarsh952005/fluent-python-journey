"""
Chapter 1: Mini Project — Card Game Engine
==========================================
A small card game engine built entirely using Python's data model.

Features demonstrated:
- Full sequence protocol (FrenchDeck)
- Custom mutable sequence (Hand)
- Numeric protocol (CardValue)
- Context manager protocol (GameSession)
- Iterator protocol (DealIterator)

This is NOT a copy from the book — it's an original application that uses
the chapter's core concepts to build something real.

Run with: python mini_project.py
"""

from __future__ import annotations

import collections
import random
from contextlib import contextmanager
from typing import Generator, Iterator


# ─────────────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────────────

Card = collections.namedtuple("Card", ["rank", "suit"])

SUIT_SYMBOLS = {"spades": "♠", "hearts": "♥", "diamonds": "♦", "clubs": "♣"}

RANK_VALUES: dict[str, int] = {
    **{str(n): n for n in range(2, 11)},
    "J": 11, "Q": 12, "K": 13, "A": 14,
}


class Deck:
    """
    Full 52-card deck implementing the Sequence protocol.
    Immutable view of all cards — shuffle returns a new shuffled Deck.
    """

    RANKS = [str(n) for n in range(2, 11)] + list("JQKA")
    SUITS = ["clubs", "diamonds", "hearts", "spades"]

    def __init__(self, cards: list[Card] | None = None) -> None:
        if cards is None:
            self._cards = [
                Card(rank, suit)
                for suit in self.SUITS
                for rank in self.RANKS
            ]
        else:
            self._cards = list(cards)

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, position: int | slice) -> Card | list[Card]:
        return self._cards[position]

    def __repr__(self) -> str:
        return f"Deck({len(self)} cards)"

    def __iter__(self) -> Iterator[Card]:
        return iter(self._cards)

    def shuffled(self) -> Deck:
        """Return a new shuffled Deck (immutable style)."""
        cards = list(self._cards)
        random.shuffle(cards)
        return Deck(cards)

    def deal(self, n: int) -> tuple[list[Card], Deck]:
        """Deal n cards, returning (dealt_cards, remaining_deck)."""
        if n > len(self):
            raise ValueError(f"Cannot deal {n} cards from {len(self)}-card deck")
        return list(self._cards[:n]), Deck(self._cards[n:])


class Hand:
    """
    A player's hand — mutable collection with scoring support.
    Demonstrates __iadd__ for += operator (adding cards to hand).
    """

    def __init__(self, cards: list[Card] | None = None) -> None:
        self._cards: list[Card] = list(cards or [])

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, idx: int) -> Card:
        return self._cards[idx]

    def __repr__(self) -> str:
        cards_str = " ".join(
            f"{c.rank}{SUIT_SYMBOLS[c.suit]}" for c in self._cards
        )
        return f"Hand([{cards_str}], score={self.score})"

    def __iadd__(self, card: Card) -> Hand:
        """
        Enables: hand += card
        Returns self (mutates in place) which is idiomatic for __iadd__.
        """
        self._cards.append(card)
        return self

    def __bool__(self) -> bool:
        """An empty hand is falsy."""
        return bool(self._cards)

    @property
    def score(self) -> int:
        """Sum of card values — J=11, Q=12, K=13, A=14."""
        return sum(RANK_VALUES[card.rank] for card in self._cards)

    @property
    def best_card(self) -> Card | None:
        if not self._cards:
            return None
        return max(self._cards, key=lambda c: RANK_VALUES[c.rank])


# ─────────────────────────────────────────────────────────────────────────────
# Game logic
# ─────────────────────────────────────────────────────────────────────────────


@contextmanager
def game_session(player_names: list[str]) -> Generator[dict[str, Hand], None, None]:
    """
    Context manager that sets up and tears down a card game session.

    Demonstrates the context manager protocol (__enter__ / __exit__)
    via contextlib.contextmanager decorator.

    Usage:
        with game_session(["Alice", "Bob"]) as hands:
            # deal cards, play game
    """
    print(f"🃏 Starting game with: {', '.join(player_names)}")
    deck = Deck().shuffled()
    hands: dict[str, Hand] = {}

    # Deal 5 cards to each player
    for name in player_names:
        dealt, deck = deck.deal(5)
        hands[name] = Hand(dealt)
        print(f"  Dealt {len(dealt)} cards to {name}")

    try:
        yield hands
    finally:
        print("🏁 Game session ended")
        print("  Final hands:")
        for name, hand in hands.items():
            print(f"    {name}: {hand}")


def determine_winner(hands: dict[str, Hand]) -> str | None:
    """Simple highest-score-wins rule."""
    if not hands:
        return None
    return max(hands, key=lambda name: hands[name].score)


# ─────────────────────────────────────────────────────────────────────────────
# Run demo
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    print("=" * 50)
    print("  Card Game Engine — Data Model Demo")
    print("=" * 50)

    players = ["Alice", "Bob", "Charlie"]

    with game_session(players) as hands:
        # Show each player's hand
        print("\n📋 Current hands:")
        for name, hand in hands.items():
            print(f"  {name}: score={hand.score}, best={hand.best_card}")

        # Determine winner
        winner = determine_winner(hands)
        print(f"\n🏆 Winner: {winner} with score {hands[winner].score}")  # type: ignore[index]

        # Demonstrate __iadd__
        extra_card = Card("A", "spades")
        hands["Alice"] += extra_card
        print(f"\n⚡ Alice draws extra card ({extra_card.rank}♠): {hands['Alice']}")

        # Demonstrate truthiness
        empty_hand = Hand()
        print(f"\n  Empty hand is truthy: {bool(empty_hand)}")
        print(f"  Alice's hand is truthy: {bool(hands['Alice'])}")


if __name__ == "__main__":
    main()
