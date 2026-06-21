"""
Chapter 7: Functions as First-Class Objects
===========================================
Original implementations demonstrating functional programming patterns in Python.

Key concepts covered:
- Treating functions as objects (assignment, higher-order functions)
- Implementing __call__ for stateful function-like objects
- Advanced parameter signatures (/, *, **kwargs)
- Functional primitives: operator module and functools.partial
- Modern alternatives to map/filter/reduce
"""

import sys
import collections
from typing import Callable, Any
from operator import itemgetter, attrgetter, methodcaller
import functools

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Part 1: Higher-Order Functions & Modern Replacements
# ─────────────────────────────────────────────────────────────────────────────

def demo_higher_order() -> None:
    section("Part 1: Higher-Order Functions & Modern Replacements")

    # Data: A list of words to process
    words = ["strawberry", "fig", "apple", "cherry", "raspberry", "banana"]
    
    # 1. Treating functions as objects
    sorter: Callable = sorted
    
    # 2. Passing function as an argument (key)
    # Sorting by length
    by_len = sorter(words, key=len)
    print(f"Sorted by length: {by_len}")
    
    # Sorting by reversed spelling using a lambda
    by_rev = sorter(words, key=lambda w: w[::-1])
    print(f"Sorted by reverse: {by_rev}")
    
    # 3. Modern replacements for map/filter
    # Old way (map + filter with lambda)
    old_way = list(map(str.upper, filter(lambda w: len(w) > 5, words)))
    
    # New way (list comprehension - preferred for readability)
    new_way = [w.upper() for w in words if len(w) > 5]
    
    print(f"\nLong words upper (map/filter): {old_way}")
    print(f"Long words upper (listcomp):   {new_way}")
    assert old_way == new_way


# ─────────────────────────────────────────────────────────────────────────────
# Part 2: User-Defined Callables (__call__)
# ─────────────────────────────────────────────────────────────────────────────

class RateLimiter:
    """A callable object that maintains state across calls.
    Demonstrates that any class with __call__ acts like a function.
    """
    def __init__(self, max_calls: int):
        self.max_calls = max_calls
        self.calls = 0
        
    def __call__(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        if self.calls >= self.max_calls:
            raise RuntimeError("Rate limit exceeded")
        self.calls += 1
        return func(*args, **kwargs)

def demo_callables() -> None:
    section("Part 2: User-Defined Callables (__call__)")
    
    limiter = RateLimiter(max_calls=2)
    
    print(f"Is limiter callable? {callable(limiter)}")
    
    def fetch_data(id: int) -> str:
        return f"Data for {id}"
        
    print(limiter(fetch_data, 1))  # Call 1
    print(limiter(fetch_data, 2))  # Call 2
    
    try:
        limiter(fetch_data, 3)     # Call 3 (should fail)
    except RuntimeError as e:
        print(f"Expected error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Part 3: Advanced Parameter Signatures
# ─────────────────────────────────────────────────────────────────────────────

# Notice the signature:
# a, b: positional-only (requires Python 3.8+)
# c: positional or keyword
# *: indicates all following are keyword-only
# d: keyword-only
# **kwargs: captures remaining keyword args
def complex_signature(a, b, /, c, *, d, **kwargs):
    """Demonstrates positional-only and keyword-only parameters."""
    return f"a={a}, b={b}, c={c}, d={d}, kwargs={kwargs}"

def demo_signatures() -> None:
    section("Part 3: Advanced Parameter Signatures")
    
    # Valid call
    res = complex_signature(1, 2, 3, d=4, e=5)
    print(f"Valid call: {res}")
    
    # Positional-only prevents passing a, b as keywords
    try:
        complex_signature(a=1, b=2, c=3, d=4)
    except TypeError as e:
        print(f"Expected TypeError (positional-only): {e}")
        
    # Keyword-only prevents passing d as positional
    try:
        complex_signature(1, 2, 3, 4)
    except TypeError as e:
        print(f"Expected TypeError (keyword-only): {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Part 4: Functional Primitives (operator & functools)
# ─────────────────────────────────────────────────────────────────────────────

def demo_functional_primitives() -> None:
    section("Part 4: Functional Primitives (operator & functools.partial)")
    
    # Data: List of namedtuples
    City = collections.namedtuple('City', 'name country pop coordinates')
    cities = [
        City('Tokyo', 'JP', 36.933, (35.689722, 139.691667)),
        City('Delhi NCR', 'IN', 21.935, (28.613889, 77.208889)),
        City('Mexico City', 'MX', 20.142, (19.433333, -99.133333)),
    ]
    
    # 1. itemgetter: sorting by index (country code)
    by_country = sorted(cities, key=itemgetter(1))
    print(f"Sorted by country code (itemgetter): {[c.name for c in by_country]}")
    
    # 2. attrgetter: sorting by nested attribute
    # operator replaces the need for: lambda c: c.coordinates[0]
    by_lat = sorted(cities, key=attrgetter('coordinates'))
    print(f"Sorted by latitude (attrgetter): {[c.name for c in by_lat]}")
    
    # 3. methodcaller: invoking a method on items
    s = "The time has come"
    upcase = methodcaller('upper')
    replace_spaces = methodcaller('replace', ' ', '-')
    
    print(f"\nmethodcaller('upper'): {upcase(s)}")
    print(f"methodcaller('replace'): {replace_spaces(s)}")
    
    # 4. functools.partial: freezing arguments
    # Create a new function that always multiplies by 3
    import operator
    triple = functools.partial(operator.mul, 3)
    
    print(f"\nfunctools.partial(mul, 3)(7) -> {triple(7)}")
    
    # Useful for callback APIs that expect 0-arg or 1-arg functions
    # e.g., freezing a tag generator
    def tag(name, content, class_=None):
        cls_attr = f' class="{class_}"' if class_ else ''
        return f'<{name}{cls_attr}>{content}</{name}>'
        
    p_tag = functools.partial(tag, 'p', class_='paragraph')
    print(f"Partial tag generator: {p_tag('Hello World!')}")


if __name__ == "__main__":
    demo_higher_order()
    demo_callables()
    demo_signatures()
    demo_functional_primitives()
