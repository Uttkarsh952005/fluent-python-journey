"""
Chapter 23: Mini Project — Simulated ORM Framework
==================================================
Demonstrating how libraries like Django ORM or SQLAlchemy build their 
declarative models using Attribute Descriptors.

We build an abstract `Field` descriptor, and concrete `CharField` and
`IntegerField` descriptors to validate data cleanly.
"""

import sys
import abc

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# The Descriptor Framework
# ─────────────────────────────────────────────────────────────────────────────

class Field(abc.ABC):
    """Abstract base class for all ORM fields."""
    
    def __set_name__(self, owner, name):
        self.storage_name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.storage_name)

    def __set__(self, instance, value):
        # We call our abstract validator before saving the data
        self.validate(value)
        instance.__dict__[self.storage_name] = value

    @abc.abstractmethod
    def validate(self, value):
        """Must be implemented by subclasses to enforce type safety."""
        pass


class CharField(Field):
    """Ensures the assigned value is a string under the max length."""
    
    def __init__(self, max_length: int):
        self.max_length = max_length

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.storage_name} must be a string")
        if len(value) > self.max_length:
            raise ValueError(f"{self.storage_name} exceeds max length of {self.max_length}")


class IntegerField(Field):
    """Ensures the assigned value is a positive integer."""
    
    def validate(self, value):
        if not isinstance(value, int):
            raise TypeError(f"{self.storage_name} must be an integer")
        if value < 0:
            raise ValueError(f"{self.storage_name} cannot be negative")

# ─────────────────────────────────────────────────────────────────────────────
# The Managed Model
# ─────────────────────────────────────────────────────────────────────────────

class User:
    # Look at how clean the class definition is! 
    # All validation logic is completely abstracted into the descriptors.
    username = CharField(max_length=15)
    age = IntegerField()

    def __init__(self, username, age):
        self.username = username
        self.age = age

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Execution
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Simulated ORM using Descriptors")
    print("=" * 60)

    print("Creating User(username='Alice', age=28)...")
    alice = User("Alice", 28)
    print(f"  Success! Username: {alice.username}, Age: {alice.age}")
    
    print("\nAttempting to set age to a string ('thirty')...")
    try:
        alice.age = "thirty"
    except TypeError as e:
        print(f"  [Caught] {e}")

    print("\nAttempting to set username to 20 characters...")
    try:
        alice.username = "ThisIsWayTooLongForAUsername"
    except ValueError as e:
        print(f"  [Caught] {e}")

if __name__ == "__main__":
    main()
