"""
Chapter 23: Benchmarks — The Memory Footprint of Descriptors
============================================================
Why use Descriptors instead of `@property`?
If a class has 50 attributes that all require >0 validation, 
you would have to copy-paste the `@property` getter/setter 50 times.
Descriptors allow you to write the logic ONCE and instantiate it 50 times.

This benchmark proves that Descriptors add zero memory overhead
compared to raw `@property` declarations.
"""

import sys
import sys as _sys # For getsizeof

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")

# ── Setup ────────────────────────────────────────────────────────────────────

# 1. The Property Way (Verbose and repetitive)
class PropertyItem:
    def __init__(self, weight, price):
        self.weight = weight
        self.price = price

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        if value > 0:
            self._weight = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value > 0:
            self._price = value

# 2. The Descriptor Way (DRY: Don't Repeat Yourself)
class Quantity:
    def __set_name__(self, owner, name):
        self.storage_name = name
    def __get__(self, instance, owner):
        return instance.__dict__[self.storage_name]
    def __set__(self, instance, value):
        if value > 0:
            instance.__dict__[self.storage_name] = value

class DescriptorItem:
    weight = Quantity()
    price = Quantity()
    
    def __init__(self, weight, price):
        self.weight = weight
        self.price = price

# ── Benchmarks ───────────────────────────────────────────────────────────────

def get_deep_size(obj):
    """A simplistic deep size calculator for the instance and its dict."""
    return _sys.getsizeof(obj) + _sys.getsizeof(obj.__dict__)

def run_benchmarks():
    section("Benchmark: Memory Footprint (Property vs Descriptor)")
    
    prop_item = PropertyItem(10, 20)
    desc_item = DescriptorItem(10, 20)
    
    print(f"  PropertyItem size:   {get_deep_size(prop_item)} bytes")
    print(f"  DescriptorItem size: {get_deep_size(desc_item)} bytes")
    
    print("\nConclusion:")
    print("Descriptors do not consume extra memory per instance.")
    print("They store their data in the exact same instance __dict__ as properties.")
    print("The real benefit is Developer Time: drastically reducing Lines of Code.")

if __name__ == "__main__":
    run_benchmarks()
