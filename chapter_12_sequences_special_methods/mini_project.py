"""
Chapter 12: Mini Project — A Pythonic TimeSeries Object
=======================================================
A practical application of Sequence protocols. We build a TimeSeries 
object that supports slicing, sequence iteration, and dynamic attribute 
access for basic analytics (e.g., ts.max, ts.min).
"""

import sys
from array import array

sys.stdout.reconfigure(encoding="utf-8")

class TimeSeries:
    """
    A sequence of numerical data points representing a time series.
    Supports native slicing, iteration, and dynamic property routing.
    """
    
    # Allowed dynamic attributes
    _aggregates = {'min': min, 'max': max, 'sum': sum}

    def __init__(self, name: str, data: list[float]):
        self.name = name
        self._data = array('d', data)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index):
        cls = type(self)
        if isinstance(index, slice):
            # Maintain the sequence type when sliced, preserve the name
            sliced_data = self._data[index]
            return cls(f"{self.name}_slice", sliced_data)
        elif isinstance(index, int):
            return self._data[index]
        else:
            raise TypeError(f"{cls.__name__} indices must be integers or slices")

    def __getattr__(self, name: str):
        # Dynamically compute aggregates if requested
        if name in self._aggregates:
            if not self._data:
                raise ValueError(f"Cannot compute {name} on an empty TimeSeries")
            # Apply the mapped function (min, max, sum) to our data
            func = self._aggregates[name]
            return func(self._data)
            
        # Fallback to standard error
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    def __setattr__(self, name: str, value):
        # Prevent users from overwriting our dynamic aggregates
        if name in self._aggregates:
            raise AttributeError(f"Cannot overwrite dynamic aggregate property {name!r}")
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        data_preview = repr(self._data.tolist()[:3])
        if len(self._data) > 3:
            data_preview = data_preview[:-1] + ", ...]"
        return f"TimeSeries({self.name!r}, {data_preview})"


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TimeSeries API Demonstration")
    print("=" * 60)

    # 1. Instantiate
    prices = TimeSeries("AAPL_closing", [150.2, 151.0, 149.5, 155.0, 157.2, 160.1, 159.0])
    print(f"Original: {prices!r}")
    print(f"Length:   {len(prices)}")

    # 2. Sequence Iteration & Slicing
    q1_prices = prices[:3]
    print(f"Sliced:   {q1_prices!r} (Note it returned a new TimeSeries!)")
    
    print("\nIterating over slice:")
    for i, price in enumerate(q1_prices):
        print(f"  Day {i+1}: ${price}")

    # 3. Dynamic Attributes (__getattr__)
    print("\nDynamic Analytics via __getattr__:")
    print(f"  Max Price: ${prices.max}")
    print(f"  Min Price: ${prices.min}")
    print(f"  Sum Price: ${prices.sum:.2f}")

    # 4. Shadowing Prevention (__setattr__)
    try:
        prices.max = 999.0
    except AttributeError as e:
        print(f"\nCaught shadowing attempt: {e}")

if __name__ == "__main__":
    main()
