"""
Chapter 24: Class Metaprogramming
=================================
Original implementations exploring how to write code that writes code.
We explore three tiers of class metaprogramming: Class Decorators,
the modern __init_subclass__, and the nuclear option: Metaclasses.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Class Decorators
# ─────────────────────────────────────────────────────────────────────────────

def add_timestamp(cls):
    """A Class Decorator that injects a new attribute AFTER creation."""
    cls.timestamp = "2026-06-21 00:00:00"
    return cls

@add_timestamp
class Document:
    pass


# ─────────────────────────────────────────────────────────────────────────────
# 2. __init_subclass__ (Python 3.6+)
# ─────────────────────────────────────────────────────────────────────────────

class PluginRegistry:
    """
    Any class that inherits from PluginRegistry will automatically
    be added to this dictionary the moment it is defined!
    """
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # We automatically register the subclass name mapped to the class itself
        cls.registry[cls.__name__] = cls


class ImagePlugin(PluginRegistry):
    pass

class AudioPlugin(PluginRegistry):
    pass


# ─────────────────────────────────────────────────────────────────────────────
# 3. Metaclasses (The Nuclear Option)
# ─────────────────────────────────────────────────────────────────────────────

class ValidationMeta(type):
    """
    A Metaclass MUST inherit from `type`.
    It executes *during* the physical creation of the class in memory.
    """
    def __new__(meta_cls, cls_name, bases, cls_dict):
        # We can intercept the class dictionary BEFORE the class exists!
        for name, value in cls_dict.items():
            # Rule: No methods are allowed to have uppercase letters.
            if callable(value) and any(c.isupper() for c in name):
                raise SyntaxError(f"Method '{name}' in '{cls_name}' must be completely lowercase.")
        
        # Finally, ask `type` to physically construct the class
        return super().__new__(meta_cls, cls_name, bases, cls_dict)


class StrictModel(metaclass=ValidationMeta):
    
    def valid_method(self):
        pass
        
    # Uncommenting the following line would instantly crash the program 
    # at IMPORT time, before this class is ever even instantiated!
    
    # def InvalidMethod(self): pass


def demo_metaprogramming() -> None:
    section("Part 1: Class Decorators")
    print(f"  Document.timestamp: {Document.timestamp}")
    
    section("Part 2: __init_subclass__ (Automatic Registry)")
    print(f"  Registered Plugins: {list(PluginRegistry.registry.keys())}")
    
    section("Part 3: Metaclasses")
    print("  StrictModel compiled successfully because all methods are lowercase.")
    print("  (Validation happens at import time, not runtime!)")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_metaprogramming()
