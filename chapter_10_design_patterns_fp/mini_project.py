"""
Chapter 10: Mini Project — Functional E-Commerce Checkout
=========================================================
A practical implementation combining functional Strategy and Command
patterns into a clean e-commerce checkout pipeline.

Concepts demonstrated:
- Functions as Strategies (promotions)
- Functions as Commands (event dispatching)
- Decoupling logic without heavy abstract base classes
"""

import sys
from typing import Callable
from decimal import Decimal

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Functional Strategies (The Discounts)
# ─────────────────────────────────────────────────────────────────────────────
# A promotion is any function that takes a Cart and returns a discount amount.

def promo_black_friday(cart: 'Cart') -> Decimal:
    return cart.subtotal * Decimal("0.30")  # 30% off everything

def promo_bulk_buy(cart: 'Cart') -> Decimal:
    if len(cart.items) >= 5:
        return cart.subtotal * Decimal("0.15")  # 15% off for 5+ items
    return Decimal("0.0")

def promo_loyalty(cart: 'Cart') -> Decimal:
    if cart.customer.is_loyalty:
        return cart.subtotal * Decimal("0.05")  # 5% off for members
    return Decimal("0.0")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Functional Commands (The Event Hooks)
# ─────────────────────────────────────────────────────────────────────────────
# A command is any function to execute after checkout.

def hook_send_email(cart: 'Cart') -> None:
    print(f"  [Email] Receipt sent to {cart.customer.name}")

def hook_update_inventory(cart: 'Cart') -> None:
    print(f"  [Inventory] Deducted {len(cart.items)} items from stock")

def hook_award_points(cart: 'Cart') -> None:
    if cart.customer.is_loyalty:
        points = int(cart.total_due)
        print(f"  [Loyalty] Awarded {points} points to {cart.customer.name}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. The Context (The Cart)
# ─────────────────────────────────────────────────────────────────────────────

class Customer:
    def __init__(self, name: str, is_loyalty: bool):
        self.name = name
        self.is_loyalty = is_loyalty

class Cart:
    def __init__(self, customer: Customer):
        self.customer = customer
        self.items: list[Decimal] = []
        # Strategy: a single callable
        self.promotion: Callable[['Cart'], Decimal] | None = None
        # Commands: a list of callables
        self.on_checkout_hooks: list[Callable[['Cart'], None]] = []

    def add_item(self, price: str) -> None:
        self.items.append(Decimal(price))

    @property
    def subtotal(self) -> Decimal:
        return sum(self.items)

    @property
    def total_due(self) -> Decimal:
        discount = self.promotion(self) if self.promotion else Decimal("0.0")
        return self.subtotal - discount

    def checkout(self) -> None:
        print(f"\nProcessing checkout for {self.customer.name}...")
        print(f"  Subtotal: ${self.subtotal:.2f}")
        print(f"  Total Due: ${self.total_due:.2f}")
        
        # Execute the Command Queue
        for hook in self.on_checkout_hooks:
            hook(self)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Functional E-Commerce Checkout")
    print("=" * 60)

    alice = Customer("Alice", is_loyalty=True)
    bob = Customer("Bob", is_loyalty=False)

    # Alice's Cart: Uses Black Friday Strategy and 3 Event Hooks
    cart1 = Cart(alice)
    for _ in range(3): cart1.add_item("20.00")
    cart1.promotion = promo_black_friday
    cart1.on_checkout_hooks.extend([
        hook_send_email, 
        hook_update_inventory, 
        hook_award_points
    ])
    cart1.checkout()

    # Bob's Cart: Uses Bulk Buy Strategy and 2 Event Hooks
    cart2 = Cart(bob)
    for _ in range(6): cart2.add_item("10.00")
    cart2.promotion = promo_bulk_buy
    cart2.on_checkout_hooks.extend([
        hook_send_email, 
        hook_update_inventory
    ])
    cart2.checkout()


if __name__ == "__main__":
    main()
