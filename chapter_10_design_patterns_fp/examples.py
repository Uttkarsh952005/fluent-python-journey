"""
Chapter 10: Design Patterns with First-Class Functions
======================================================
Original implementations demonstrating the refactoring of classic
Gang of Four (GoF) design patterns using Python's functional capabilities.

Key concepts covered:
- The Classic OOP Strategy Pattern (using ABCs)
- Refactoring Strategy to use first-class functions
- Dynamic strategy selection
- The Command Pattern via Callables
"""

import sys
from abc import ABC, abstractmethod
from typing import Callable

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Part 1: The Classic OOP Strategy Pattern
# ─────────────────────────────────────────────────────────────────────────────

class Order:
    """The Context in the Strategy pattern."""
    def __init__(self, customer: str, total: float, strategy: 'DiscountStrategy' = None):
        self.customer = customer
        self.total = total
        self.strategy = strategy

    def due(self) -> float:
        if self.strategy:
            discount = self.strategy.discount(self)
        else:
            discount = 0.0
        return self.total - discount

class DiscountStrategy(ABC):
    """The Strategy abstract base class."""
    @abstractmethod
    def discount(self, order: Order) -> float:
        pass

class VIPDiscount(DiscountStrategy):
    """A concrete strategy."""
    def discount(self, order: Order) -> float:
        return order.total * 0.2

class BulkItemDiscount(DiscountStrategy):
    """Another concrete strategy."""
    def discount(self, order: Order) -> float:
        return order.total * 0.1 if order.total >= 100 else 0.0

def demo_classic_strategy() -> None:
    section("Part 1: Classic OOP Strategy Pattern")
    order = Order("Alice", 150.0, VIPDiscount())
    print(f"VIP Order due: ${order.due():.2f}")
    
    order2 = Order("Bob", 150.0, BulkItemDiscount())
    print(f"Bulk Order due: ${order2.due():.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Part 2: Refactoring Strategy with First-Class Functions
# ─────────────────────────────────────────────────────────────────────────────
# In Python, we don't need a single-method class. The strategy can just be a function.

# Type alias for our function-based strategy
PromotionFunc = Callable[['FuncOrder'], float]

class FuncOrder:
    def __init__(self, customer: str, total: float, promotion: PromotionFunc = None):
        self.customer = customer
        self.total = total
        self.promotion = promotion

    def due(self) -> float:
        if self.promotion:
            discount = self.promotion(self)
        else:
            discount = 0.0
        return self.total - discount

def vip_promo(order: FuncOrder) -> float:
    return order.total * 0.2

def bulk_promo(order: FuncOrder) -> float:
    return order.total * 0.1 if order.total >= 100 else 0.0

def demo_functional_strategy() -> None:
    section("Part 2: Function-Based Strategy Pattern")
    # Notice how we just pass the function itself, no instantiation required!
    order1 = FuncOrder("Alice", 150.0, vip_promo)
    print(f"VIP Order due: ${order1.due():.2f}")
    
    order2 = FuncOrder("Bob", 150.0, bulk_promo)
    print(f"Bulk Order due: ${order2.due():.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Part 3: Dynamic Strategy Selection
# ─────────────────────────────────────────────────────────────────────────────
# We can iterate over functions to find the best strategy!

PROMOS = [vip_promo, bulk_promo]

def best_promo(order: FuncOrder) -> float:
    """Computes the best discount available."""
    return max(promo(order) for promo in PROMOS)

def demo_best_strategy() -> None:
    section("Part 3: Dynamic Best Strategy")
    # Alice gets the best of both worlds (VIP 20% beats Bulk 10%)
    order = FuncOrder("Alice", 150.0, best_promo)
    print(f"Order using best_promo due: ${order.due():.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Part 4: The Command Pattern via Callables
# ─────────────────────────────────────────────────────────────────────────────
# Instead of Invoker -> Command.execute() -> Receiver,
# we just do Invoker -> Callable() -> Receiver

class MacroCommand:
    """A command that executes a list of commands."""
    def __init__(self, commands: list[Callable]):
        self.commands = list(commands)
        
    def __call__(self):
        for command in self.commands:
            command()

def demo_command() -> None:
    section("Part 4: Command Pattern via Callables")
    
    def turn_on_lights(): print("Lights ON")
    def play_music(): print("Music PLAYING")
    
    # The MacroCommand acts as the Invoker
    party_mode = MacroCommand([turn_on_lights, play_music])
    
    print("Activating Party Mode:")
    party_mode()


if __name__ == "__main__":
    demo_classic_strategy()
    demo_functional_strategy()
    demo_best_strategy()
    demo_command()
