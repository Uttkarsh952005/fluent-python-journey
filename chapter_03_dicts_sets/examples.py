"""
Chapter 3: Dicts and Sets -- Examples
======================================
Original implementations with deep annotations covering:

  Part 1  -- Dict construction idioms
  Part 2  -- Missing key handling: get, setdefault, defaultdict, __missing__
  Part 3  -- Specialized dict variants: Counter, ChainMap, OrderedDict
  Part 4  -- Dict views and set-like operations
  Part 5  -- Set and frozenset fundamentals
  Part 6  -- Hash protocol: __hash__ and __eq__ contract
  Part 7  -- Dict merge operators (Python 3.9+)

Run with: python examples.py
"""

from __future__ import annotations

import sys
from collections import ChainMap, Counter, OrderedDict, defaultdict
from typing import Any, Hashable, Iterator

sys.stdout.reconfigure(encoding="utf-8")


# =============================================================================
# PART 1: Dict Construction Idioms
# =============================================================================

def dict_construction_demo() -> None:
    """
    Python gives you five ways to build a dict.
    Each communicates intent differently.
    """
    print("=== Part 1: Dict Construction ===\n")

    # Literal -- most common, most readable
    by_literal = {"name": "Alice", "age": 30, "city": "Tokyo"}

    # dict() constructor with keyword args -- only works for string keys
    by_kwargs = dict(name="Alice", age=30, city="Tokyo")

    # dict() from iterable of (key, value) pairs
    by_pairs = dict([("name", "Alice"), ("age", 30), ("city", "Tokyo")])

    # Dict comprehension -- transform another mapping or iterable
    words = ["apple", "banana", "cherry"]
    word_lengths = {w: len(w) for w in words}

    # Zip two sequences into a dict
    keys = ["a", "b", "c"]
    values = [1, 2, 3]
    by_zip = dict(zip(keys, values))

    print(f"by_literal:  {by_literal}")
    print(f"by_kwargs:   {by_kwargs}")
    print(f"by_pairs:    {by_pairs}")
    print(f"word_lengths:{word_lengths}")
    print(f"by_zip:      {by_zip}")

    # All produce equal dicts
    assert by_literal == by_kwargs == by_pairs
    print("\nAll three construction methods produce equal dicts: True")

    # Dict comprehension with filter
    long_words = {w: len(w) for w in words if len(w) > 5}
    print(f"Words longer than 5 chars: {long_words}")

    # Inverting a dict (assumes values are unique and hashable)
    original = {"a": 1, "b": 2, "c": 3}
    inverted = {v: k for k, v in original.items()}
    print(f"\nOriginal: {original}")
    print(f"Inverted: {inverted}")


# =============================================================================
# PART 2: Missing Key Handling
# =============================================================================

def missing_key_demo() -> None:
    """
    Four strategies for handling missing keys -- each suited to different situations.

    Strategy 1: dict.get(key, default)    -- one-off safe access
    Strategy 2: dict.setdefault(key, [])  -- build nested structures
    Strategy 3: defaultdict               -- always-present default factory
    Strategy 4: __missing__ override      -- custom dict subclass logic
    """
    print("\n=== Part 2: Missing Key Handling ===\n")

    # --- Strategy 1: get() ---
    inventory = {"apples": 10, "oranges": 5}

    # Without get() -- requires key check
    count_old = inventory["bananas"] if "bananas" in inventory else 0

    # With get() -- cleaner
    count_new = inventory.get("bananas", 0)

    print(f"[get()] bananas: {count_new}  (old style was: {count_old})")

    # --- Strategy 2: setdefault() ---
    # GOAL: build a dict mapping each letter to the list of words containing it.
    # setdefault() avoids a repeated key check + assignment.

    words = ["apple", "banana", "avocado", "blueberry", "cherry"]
    index: dict[str, list[str]] = {}

    for word in words:
        for letter in word:
            # Equivalent to:
            #   if letter not in index: index[letter] = []
            #   index[letter].append(word)
            # But in ONE dict lookup instead of two:
            index.setdefault(letter, []).append(word)

    print(f"\n[setdefault()] Words with 'a': {index.get('a', [])}")
    print(f"[setdefault()] Words with 'b': {index.get('b', [])}")

    # --- Strategy 3: defaultdict ---
    # defaultdict auto-creates the default value on first access.
    # The factory is called with NO arguments when a missing key is accessed.

    dd: defaultdict[str, list[str]] = defaultdict(list)
    for word in words:
        for letter in word:
            dd[letter].append(word)  # No setdefault needed!

    print(f"\n[defaultdict(list)] Words with 'c': {dd['c']}")
    print(f"[defaultdict(list)] Accessing missing key 'z': {dd['z']}")
    print(f"  'z' is now in dd: {'z' in dd}")  # True! It was auto-created

    # defaultdict(int) -- elegant word counter
    text = "the cat sat on the mat the cat"
    freq: defaultdict[str, int] = defaultdict(int)
    for word in text.split():
        freq[word] += 1  # Missing key starts at 0 automatically
    print(f"\n[defaultdict(int)] Word frequencies: {dict(freq)}")

    # --- Strategy 4: __missing__ override ---
    # Called by __getitem__ when key is not found.
    # DOES NOT trigger on .get() -- important distinction!

    class FoldedDict(dict):
        """
        A dict that treats string keys as case-insensitive.
        Missing key lookup folds to lowercase before giving up.

        This demonstrates __missing__ -- the hook called by dict.__getitem__
        when a key is not found.
        """
        def __missing__(self, key: str) -> Any:
            if isinstance(key, str):
                folded = key.lower()
                if folded in self:
                    return self[folded]
            raise KeyError(key)

        def __contains__(self, key: object) -> bool:
            if isinstance(key, str):
                return dict.__contains__(self, key) or dict.__contains__(self, key.lower())
            return dict.__contains__(self, key)

    fd = FoldedDict({"name": "Alice", "city": "Tokyo"})
    print(f"\n[__missing__] fd['NAME']: {fd['NAME']}")
    print(f"[__missing__] fd['CITY']: {fd['CITY']}")
    print(f"[__missing__] fd.get('NAME'): {fd.get('NAME')}")  # None! get() skips __missing__

    # KEY INSIGHT: __missing__ is ONLY called by __getitem__ (fd[key]).
    # fd.get(), 'key' in fd, update() -- do NOT trigger __missing__.
    print("  Note: get() returned None -- __missing__ is NOT called by get()")


# =============================================================================
# PART 3: Specialized Dict Variants
# =============================================================================

def specialized_dicts_demo() -> None:
    """
    Counter, ChainMap, and OrderedDict -- each solves a specific problem
    that a plain dict handles clumsily.
    """
    print("\n=== Part 3: Specialized Dict Variants ===\n")

    # --- Counter ---
    # A multiset (bag) implementation. Maps elements to their counts.
    # Optimized for counting operations.

    text = "she sells seashells by the seashore"
    word_count = Counter(text.split())
    print(f"[Counter] Word counts: {dict(word_count)}")
    print(f"[Counter] 3 most common: {word_count.most_common(3)}")

    # Counter supports arithmetic
    c1 = Counter("aaabbc")
    c2 = Counter("abbccc")
    print(f"\n[Counter] c1 + c2: {c1 + c2}")  # Add counts
    print(f"[Counter] c1 - c2: {c1 - c2}")  # Subtract (drop negatives)
    print(f"[Counter] c1 & c2: {c1 & c2}")  # Intersection (min)
    print(f"[Counter] c1 | c2: {c1 | c2}")  # Union (max)

    # Counter.update() for incremental counting
    c1.update("aaa")
    print(f"[Counter] After update('aaa'): {dict(c1)}")

    # --- ChainMap ---
    # A view over multiple mappings -- lookup searches each in order.
    # No data is copied. Writes go to the FIRST mapping only.

    defaults = {"color": "red", "user": "guest", "timeout": 30}
    env_vars = {"color": "blue", "user": "admin"}
    cli_args = {"timeout": 60}

    # Priority: cli_args > env_vars > defaults
    config = ChainMap(cli_args, env_vars, defaults)
    print(f"\n[ChainMap] color: {config['color']}")    # blue (from env_vars)
    print(f"[ChainMap] user: {config['user']}")        # admin (from env_vars)
    print(f"[ChainMap] timeout: {config['timeout']}")  # 60 (from cli_args)

    # Write goes to first map only
    config["new_key"] = "new_value"
    print(f"[ChainMap] After write, cli_args: {dict(cli_args)}")
    print(f"  defaults unchanged: {'new_key' not in defaults}")

    # Common use: implementing scoped namespaces (like Python's own scope chain)
    # child scope extends parent without copying
    parent_scope = ChainMap({"x": 1, "y": 2})
    child_scope = parent_scope.new_child({"x": 10})  # x is shadowed
    print(f"\n[ChainMap.new_child()] x in child: {child_scope['x']}")   # 10
    print(f"[ChainMap.new_child()] y in child: {child_scope['y']}")   # 2 (from parent)

    # --- OrderedDict ---
    # In Python 3.7+, plain dicts preserve insertion order.
    # OrderedDict still adds two extras:
    #   1. move_to_end() -- efficiently move a key to front or back
    #   2. Equality considers ORDER (plain dicts don't!)

    od1 = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
    od2 = OrderedDict([("c", 3), ("b", 2), ("a", 1)])
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = {"c": 3, "b": 2, "a": 1}

    print(f"\n[OrderedDict] od1 == od2: {od1 == od2}")  # False -- order matters
    print(f"[OrderedDict] d1 == d2: {d1 == d2}")        # True -- plain dict ignores order

    # move_to_end() -- useful for LRU-cache style implementations
    od1.move_to_end("a")          # Move 'a' to the END
    print(f"[OrderedDict] After move_to_end('a'): {list(od1.keys())}")
    od1.move_to_end("c", last=False)  # Move 'c' to the FRONT
    print(f"[OrderedDict] After move_to_end('c', last=False): {list(od1.keys())}")


# =============================================================================
# PART 4: Dict Views and Set-Like Operations
# =============================================================================

def dict_views_demo() -> None:
    """
    dict.keys(), dict.values(), and dict.items() return VIEW objects.
    Views are live -- they reflect changes to the dict in real time.
    keys() and items() support set operations (they contain hashable objects).
    """
    print("\n=== Part 4: Dict Views ===\n")

    inventory = {"apples": 10, "bananas": 5, "cherries": 20}
    keys_view = inventory.keys()
    items_view = inventory.items()

    print(f"keys_view:  {keys_view}")
    print(f"items_view: {items_view}")

    # Views are live -- they update when the dict changes
    inventory["dates"] = 8
    print(f"\nAfter adding 'dates':")
    print(f"  keys_view now: {keys_view}")  # Includes 'dates'!

    # keys() and items() support set operations
    store_a = {"apples": 10, "bananas": 5, "cherries": 20}
    store_b = {"bananas": 15, "cherries": 8, "dates": 12}

    # Items both stores carry
    common_items = store_a.keys() & store_b.keys()
    print(f"\n[Dict views as sets] Both stores carry: {common_items}")

    # Items only in store_a
    only_in_a = store_a.keys() - store_b.keys()
    print(f"[Dict views as sets] Only in store A: {only_in_a}")

    # All unique items across both stores
    all_items = store_a.keys() | store_b.keys()
    print(f"[Dict views as sets] All items: {all_items}")

    # IMPORTANT: values() is NOT a set-like view (values can be duplicates)
    # store_a.values() & store_b.values()  <-- TypeError!
    print("\nNote: values() does not support set operations (values may duplicate)")

    # Iterating items() is the canonical way to iterate dict key+value pairs
    print("\n[items() iteration]")
    for fruit, count in store_a.items():
        print(f"  {fruit}: {count}")


# =============================================================================
# PART 5: Set and Frozenset
# =============================================================================

def sets_demo() -> None:
    """
    set -- mutable, unordered, no duplicates, O(1) membership.
    frozenset -- immutable, hashable version of set (can be dict key or set element).
    """
    print("\n=== Part 5: Sets and Frozensets ===\n")

    # Construction
    s1 = {1, 2, 3, 4, 5}
    s2 = set([3, 4, 5, 6, 7])      # From iterable
    s3 = set()                      # MUST use set() -- {} creates empty dict!

    # Fundamental set operations
    print(f"s1: {sorted(s1)}")
    print(f"s2: {sorted(s2)}")
    print(f"Union (s1 | s2):              {sorted(s1 | s2)}")
    print(f"Intersection (s1 & s2):       {sorted(s1 & s2)}")
    print(f"Difference (s1 - s2):         {sorted(s1 - s2)}")
    print(f"Symmetric diff (s1 ^ s2):     {sorted(s1 ^ s2)}")

    # Subset and superset tests
    small = {3, 4}
    print(f"\nsmall = {small}")
    print(f"small.issubset(s1):    {small.issubset(s1)}")
    print(f"small <= s1:           {small <= s1}")  # Same as issubset
    print(f"s1.issuperset(small):  {s1.issuperset(small)}")

    # Set comprehension
    words = ["apple", "Apple", "BANANA", "banana", "Cherry"]
    unique_lower = {w.lower() for w in words}  # Deduplicates via set
    print(f"\n[Set comprehension] Unique words (case-insensitive): {sorted(unique_lower)}")

    # CRITICAL: Deduplication preserving order via dict (Python 3.7+)
    # set() loses order -- use dict.fromkeys() if order matters
    nums_with_dupes = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
    deduped_unordered = list(set(nums_with_dupes))       # Order not preserved
    deduped_ordered = list(dict.fromkeys(nums_with_dupes))  # Order preserved!
    print(f"\nOriginal:          {nums_with_dupes}")
    print(f"set() deduplicated: {sorted(deduped_unordered)} (order lost)")
    print(f"dict.fromkeys():    {deduped_ordered} (order preserved!)")

    # frozenset -- immutable, hashable
    fs = frozenset([1, 2, 3])
    print(f"\n[frozenset] {fs}, hash: {hash(fs)}")

    # frozenset can be a dict key or element of a set
    graph: dict[frozenset, str] = {
        frozenset({"A", "B"}): "edge AB",
        frozenset({"B", "C"}): "edge BC",
    }
    print(f"[frozenset as dict key] {graph[frozenset({'A', 'B'})]}")

    # A set of frozensets (e.g., unique unordered pairs)
    pairs = {frozenset({1, 2}), frozenset({2, 1}), frozenset({3, 4})}
    print(f"[set of frozensets] {len(pairs)} unique pairs: {pairs}")


# =============================================================================
# PART 6: Hash Protocol -- __hash__ and __eq__
# =============================================================================

def hash_protocol_demo() -> None:
    """
    The __hash__ / __eq__ contract is the foundation of dicts and sets.

    THE CONTRACT:
        Objects that compare equal MUST have the same hash value.
        a == b  =>  hash(a) == hash(b)

    The reverse is NOT guaranteed (hash collisions are allowed):
        hash(a) == hash(b)  does NOT mean  a == b

    CONSEQUENCES:
        - If you define __eq__, you MUST define __hash__ too.
        - Python automatically sets __hash__ = None if you define __eq__
          without __hash__, making the object unhashable.
        - Mutable objects should NOT be hashable (their hash would change).
    """
    print("\n=== Part 6: Hash Protocol ===\n")

    # Demonstrating hash consistency
    x = "hello"
    y = "hello"
    print(f"'hello' == 'hello': {x == y}")
    print(f"hash('hello') == hash('hello'): {hash(x) == hash(y)}")

    # Integers and their float equivalents have equal hashes (they compare equal)
    print(f"\nhash(1) == hash(1.0): {hash(1) == hash(1.0)}  (because 1 == 1.0)")
    print(f"hash(1): {hash(1)},  hash(1.0): {hash(1.0)}")

    # Mutable objects are not hashable -- they have no stable identity
    try:
        hash([1, 2, 3])
    except TypeError as e:
        print(f"\nhash([1,2,3]) raises: {e}")

    # --- Correct custom __hash__ implementation ---
    class Vector2D:
        """
        2D vector with correct hash/eq contract.
        Both methods use the same fields.
        """
        def __init__(self, x: float, y: float) -> None:
            self.x = x
            self.y = y

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Vector2D):
                return NotImplemented
            return self.x == other.x and self.y == other.y

        def __hash__(self) -> int:
            # hash(tuple) is stable and uses both fields
            return hash((self.x, self.y))

        def __repr__(self) -> str:
            return f"Vector2D({self.x}, {self.y})"

    v1 = Vector2D(1.0, 2.0)
    v2 = Vector2D(1.0, 2.0)
    v3 = Vector2D(3.0, 4.0)

    print(f"\n[Vector2D] v1 == v2: {v1 == v2}")
    print(f"[Vector2D] hash(v1) == hash(v2): {hash(v1) == hash(v2)}")
    print(f"[Vector2D] v1 == v3: {v1 == v3}")

    # Can be used as dict keys and set elements now
    point_labels = {v1: "origin area", v3: "far point"}
    print(f"[Vector2D as dict key] {point_labels[v2]}")  # v2 == v1, so works!

    vector_set = {v1, v2, v3}
    print(f"[Vector2D in set] {len(vector_set)} unique vectors (v1==v2, so 2)")

    # --- What happens if you only define __eq__ ---
    class BadVector:
        """Defines __eq__ but NOT __hash__ -- Python makes it unhashable."""
        def __init__(self, x: float, y: float) -> None:
            self.x, self.y = x, y

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, BadVector):
                return NotImplemented
            return self.x == other.x and self.y == other.y

    bv = BadVector(1.0, 2.0)
    print(f"\n[BadVector] has __hash__: {BadVector.__hash__ is None}")
    try:
        hash(bv)
    except TypeError as e:
        print(f"[BadVector] hash() raises: {e}")


# =============================================================================
# PART 7: Dict Merge Operators (Python 3.9+)
# =============================================================================

def dict_merge_demo() -> None:
    """
    Python 3.9 added | and |= for dict merging.
    Older alternatives: {**a, **b}, a.update(b), ChainMap.
    """
    print("\n=== Part 7: Dict Merge Operators ===\n")

    base = {"host": "localhost", "port": 5432, "db": "mydb"}
    overrides = {"port": 9999, "user": "admin"}

    # | creates a NEW dict (non-destructive)
    merged = base | overrides
    print(f"base:     {base}")
    print(f"overrides:{overrides}")
    print(f"merged (base | overrides): {merged}")
    print(f"base unchanged: {base}")

    # |= updates LEFT dict in place
    config = {"host": "localhost", "port": 5432}
    config |= {"port": 9999, "debug": True}
    print(f"\nAfter config |= ...: {config}")

    # Multiple merge -- right side wins on conflicts
    defaults  = {"timeout": 30, "retries": 3, "color": "blue"}
    user_prefs = {"color": "green", "font": "mono"}
    session   = {"timeout": 60}

    final = defaults | user_prefs | session
    print(f"\nfinal (defaults | user_prefs | session): {final}")

    # Compare with older approaches
    old_style_unpack = {**defaults, **user_prefs, **session}
    old_style_update = dict(defaults)
    old_style_update.update(user_prefs)
    old_style_update.update(session)

    assert final == old_style_unpack == old_style_update
    print("All three merge styles produce identical results: True")

    # When to use which:
    print("""
Merge style guide:
  a | b           -- new dict, non-destructive, clear intent (prefer this)
  {**a, **b}      -- also new dict, but less readable, works in Python 3.5+
  a.update(b)     -- mutates a in place, returns None (easy mistake to misread)
  a |= b          -- mutates a in place, but clear syntax (Python 3.9+)
  ChainMap(a, b)  -- no copy at all, writes go to a only (for large dicts)
""")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    dict_construction_demo()
    missing_key_demo()
    specialized_dicts_demo()
    dict_views_demo()
    sets_demo()
    hash_protocol_demo()
    dict_merge_demo()
