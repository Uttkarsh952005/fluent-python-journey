"""
Chapter 23: Attribute Descriptors
=================================
Original implementations exploring the Descriptor Protocol.
Descriptors abstract away @property methods into reusable classes,
allowing us to validate data across multiple attributes seamlessly.

Key concepts covered:
- Overriding Descriptors (__set__)
- The __set_name__ callback (Python 3.6+)
- Safe instance storage (__dict__)
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. The Quantity Descriptor (Overriding)
# ─────────────────────────────────────────────────────────────────────────────

class Quantity:
    """
    A Descriptor that ensures a value is > 0.
    Because it implements __set__, it is an 'Overriding Descriptor'.
    """
    
    def __set_name__(self, owner, name):
        """
        Called when the managed class is created.
        owner: The managed class (LineItem)
        name: The name the descriptor was assigned to ('weight' or 'price')
        """
        self.storage_name = name

    def __set__(self, instance, value):
        """
        Intercepts assignment: obj.weight = value
        instance: The managed instance (a specific LineItem)
        """
        if value > 0:
            # We MUST store the value in the managed instance's dictionary!
            # If we store it on `self` (the descriptor), it becomes global.
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError(f"{self.storage_name} must be > 0")

    def __get__(self, instance, owner):
        """
        Intercepts reading: x = obj.weight
        """
        if instance is None:
            # If accessed via the class (LineItem.weight), return the descriptor
            return self
        return instance.__dict__[self.storage_name]

# ─────────────────────────────────────────────────────────────────────────────
# 2. The Managed Class
# ─────────────────────────────────────────────────────────────────────────────

class LineItem:
    # We instantiate the descriptors as CLASS attributes.
    weight = Quantity()
    price = Quantity()

    def __init__(self, description, weight, price):
        self.description = description
        # These assignments trigger Quantity.__set__
        self.weight = weight
        self.price = price

    def subtotal(self):
        # These reads trigger Quantity.__get__
        return self.weight * self.price


def demo_descriptors() -> None:
    section("Part 1: Attribute Descriptors")
    
    item = LineItem("Truffles", 1.5, 100.0)
    print(f"  Item: {item.description}")
    print(f"  Weight: {item.weight} | Price: {item.price}")
    print(f"  Subtotal: {item.subtotal()}")
    
    print("\n  Attempting to set invalid price...")
    try:
        item.price = -50.0
    except ValueError as e:
        print(f"  Caught expected error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_descriptors()
