"""
Chapter 3: Exercises — Dicts and Sets
======================================
Original exercises extending and stress-testing chapter concepts.
These are NOT restating the examples — they push at edge cases,
implementation decisions, and patterns you'd encounter in real code.

Run with: python exercises.py
"""

from __future__ import annotations

import sys
from collections import UserDict, defaultdict
from collections.abc import Mapping
from typing import Any, Iterator

sys.stdout.reconfigure(encoding="utf-8")

# =============================================================================
# EXERCISE 1: StrKeyDict — Book's Example, Extended
# =============================================================================
#
# Ramalho walks through two versions of a dict that converts non-string keys
# to str on lookup. The second version (Example 3-9) uses UserDict.
#
# The key lesson: subclass UserDict, NOT dict, when building custom mappings.
# dict has implementation shortcuts that bypass your overridden methods.
# UserDict uses composition (self.data) and calls your __setitem__ properly.


class StrKeyDict(UserDict):
    """
    A dict that stores all keys as str.

    Ramalho's StrKeyDict from Example 3-9, with a small addition:
    we also implement __iter__ and __repr__ to make it feel complete.

    The insight: UserDict.get() calls __getitem__, which calls __missing__,
    so we get consistent behavior across d[k], d.get(k), and k in d.
    A plain dict subclass does NOT guarantee this.
    """

    def __missing__(self, key: Any) -> Any:
        # If key is already str and missing → real KeyError, stop recursion
        if isinstance(key, str):
            raise KeyError(key)
        # Otherwise, convert to str and try again via __getitem__
        return self[str(key)]

    def __contains__(self, key: object) -> bool:
        # All stored keys are str (enforced by __setitem__)
        # so we can check self.data directly — no need for self.keys()
        return str(key) in self.data

    def __setitem__(self, key: Any, item: Any) -> None:
        # Coerce ALL keys to str on insert — not just on lookup
        self.data[str(key)] = item


def exercise_1_str_key_dict() -> None:
    """
    Demonstrate StrKeyDict and explore the UserDict vs dict subclassing lesson.
    """
    print("=== Exercise 1: StrKeyDict (UserDict subclass) ===\n")

    d: StrKeyDict = StrKeyDict([("2", "two"), ("4", "four")])

    # Lookup by str key — direct
    print(f"d['2']:      {d['2']}")

    # Lookup by int key — triggers __missing__ → converts to '4' → found
    print(f"d[4]:        {d[4]}")

    # Lookup via .get() — UserDict.get() calls __getitem__, so __missing__ fires
    print(f"d.get(4):    {d.get(4)}")
    print(f"d.get(1,'?'): {d.get(1, '?')}")

    # Membership via 'in' — uses __contains__
    print(f"2 in d:      {2 in d}")    # True — str('2') is a key
    print(f"1 in d:      {1 in d}")    # False

    # __setitem__ coerces key: int 99 stored as str '99'
    d[99] = "ninety-nine"
    print(f"\nd[99] = 'ninety-nine' → stored as: {list(d.data.keys())}")
    print(f"d['99']:     {d['99']}")

    print("\nKEY INSIGHT: UserDict.get() delegates to __getitem__,")
    print("so __missing__ works for .get() too. dict subclasses don't guarantee this.")


# =============================================================================
# EXERCISE 2: Pattern Matching on Nested Records
# =============================================================================
#
# Ramalho's Example 3-2 (creator.py) shows match/case on mapping subjects.
# Key rule: mapping patterns do PARTIAL matches. Extra keys in the subject
# are silently ignored. Contrast with sequence patterns (exact length required).
#
# Also: pattern matching uses d.get(key, sentinel) internally — NOT __getitem__.
# So __missing__ is NEVER triggered during a match.


def get_creators(record: dict[str, Any]) -> list[str]:
    """
    Extract creator names from a semi-structured media record.
    Demonstrates pattern matching with partial mapping matches.
    """
    match record:
        case {"type": "book", "api": 2, "authors": [*names]}:
            return list(names)
        case {"type": "book", "api": 1, "author": str(name)}:
            return [name]
        case {"type": "book"}:
            raise ValueError(f"Invalid 'book' record: {record!r}")
        case {"type": "movie", "director": str(name)}:
            return [name]
        case _:
            raise ValueError(f"Invalid record: {record!r}")


def exercise_2_pattern_matching() -> None:
    """
    Test pattern matching on records, and show the partial-match behavior.
    """
    print("\n=== Exercise 2: Pattern Matching on Mapping Records ===\n")

    b1 = {"type": "book", "api": 1, "author": "Douglas Hofstadter",
          "title": "Godel, Escher, Bach"}   # 'title' key is extra — ignored by match
    b2 = {"type": "book", "api": 2,
          "authors": ["Martelli", "Ravenscroft", "Holden"],
          "title": "Python in a Nutshell",
          "year": 2022}                      # 'year' also extra — still matches!
    m1 = {"type": "movie", "director": "Kubrick", "year": 1968}

    print(f"b1 creators: {get_creators(b1)}")
    print(f"b2 creators: {get_creators(b2)}")
    print(f"m1 creators: {get_creators(m1)}")

    # Partial match demo: extra keys don't break the match
    print("\n[Partial match] Extra keys in b2 ('title', 'year') were silently ignored.")
    print("Mapping patterns match if the subject is a SUPERSET of the pattern keys.")

    # Show that __missing__ is never triggered in match
    class NoisyDict(dict):
        def __missing__(self, key: str) -> Any:
            print(f"  __missing__ called for key: {key!r}")
            raise KeyError(key)

    noisy = NoisyDict({"type": "book", "api": 1, "author": "X", "title": "T"})
    print(f"\n[match on NoisyDict] creators: {get_creators(noisy)}")
    print("(If __missing__ fired, you'd see output above. It didn't.)")
    print("Pattern matching uses d.get(key, sentinel), bypassing __missing__.")


# =============================================================================
# EXERCISE 3: Implement a Two-Level Priority Config
# =============================================================================
#
# Real use case: an application needs configuration from three sources
# in priority order: CLI args > environment > defaults.
#
# This exercise builds it explicitly using ChainMap semantics — but then
# adds the ability to "freeze" the resolved config into a MappingProxyType
# (Ramalho's Example 3-10) so it can't be accidentally mutated after init.


from types import MappingProxyType


class AppConfig:
    """
    Layered configuration: cli_args > env_vars > defaults.

    Uses a ChainMap for resolution, but exposes a read-only MappingProxyType
    after initialization. The proxy is dynamic — it reflects any changes
    made to the underlying layers through the mutation methods we provide.

    This is the pattern Ramalho suggests for board.pins in hardware libraries.
    """

    def __init__(
        self,
        defaults: dict[str, Any],
        env_vars: dict[str, Any] | None = None,
        cli_args: dict[str, Any] | None = None,
    ) -> None:
        from collections import ChainMap

        self._defaults = dict(defaults)
        self._env = dict(env_vars or {})
        self._cli = dict(cli_args or {})
        # Priority: cli > env > defaults
        self._chain: ChainMap[str, Any] = ChainMap(self._cli, self._env, self._defaults)
        # Read-only view over the resolved chain
        self.settings: Mapping[str, Any] = MappingProxyType(dict(self._chain))

    def _refresh(self) -> None:
        """Re-resolve and refresh the read-only proxy."""
        # MappingProxyType is dynamic only if it wraps the SAME dict object.
        # We need to update the underlying dict in place.
        resolved = dict(self._chain)
        # settings is a proxy over a dict we own — update that dict in place
        self.__dict__["settings"] = MappingProxyType(resolved)

    def set_env(self, key: str, value: Any) -> None:
        """Simulate runtime env var change."""
        self._env[key] = value
        self._chain = __import__("collections").ChainMap(
            self._cli, self._env, self._defaults
        )
        self._refresh()

    def override_cli(self, key: str, value: Any) -> None:
        """Simulate a late CLI arg override."""
        self._cli[key] = value
        self._chain = __import__("collections").ChainMap(
            self._cli, self._env, self._defaults
        )
        self._refresh()

    def __repr__(self) -> str:
        return f"AppConfig(settings={dict(self.settings)})"


def exercise_3_layered_config() -> None:
    """Show layered config with MappingProxyType for read-only exposure."""
    print("\n=== Exercise 3: Layered Config with MappingProxyType ===\n")

    cfg = AppConfig(
        defaults={"timeout": 30, "retries": 3, "color": "blue", "debug": False},
        env_vars={"color": "green", "host": "prod.example.com"},
        cli_args={"timeout": 60},
    )

    print(f"Initial config: {dict(cfg.settings)}")
    print(f"  timeout: {cfg.settings['timeout']} (cli wins over default 30)")
    print(f"  color:   {cfg.settings['color']}  (env wins over default 'blue')")
    print(f"  host:    {cfg.settings['host']}   (only in env)")

    # Show that settings is truly read-only
    try:
        cfg.settings["timeout"] = 999  # type: ignore[index]
    except TypeError as e:
        print(f"\n[Read-only] cfg.settings['timeout'] = 999 → {e}")

    # But we can mutate through the explicit API
    cfg.override_cli("debug", True)
    print(f"\nAfter override_cli('debug', True): debug = {cfg.settings['debug']}")

    cfg.set_env("color", "red")
    print(f"After set_env('color', 'red'): color = {cfg.settings['color']}")
    print("(cli has no 'color', so env 'red' wins over default 'blue')")


# =============================================================================
# EXERCISE 4: Hashability Checker and the __hash__ Contract
# =============================================================================
#
# The book explains: if you define __eq__, Python sets __hash__ = None.
# Objects that compare equal MUST have the same hash.
#
# This exercise implements a function that audits a class for hash contract
# compliance, and demonstrates what breaks when the contract is violated.


def is_hashable(obj: object) -> bool:
    """Return True if obj can be hashed without raising TypeError."""
    try:
        hash(obj)
        return True
    except TypeError:
        return False


def check_hash_contract(obj1: object, obj2: object) -> None:
    """
    If two objects compare equal, verify they have the same hash.
    Prints a warning if the contract is violated.
    """
    if obj1 == obj2:
        h1 = hash(obj1) if is_hashable(obj1) else None
        h2 = hash(obj2) if is_hashable(obj2) else None
        if h1 is None or h2 is None:
            print(f"  CONTRACT BROKEN: {obj1!r} == {obj2!r} but one/both are unhashable")
        elif h1 == h2:
            print(f"  OK: {obj1!r} == {obj2!r} and hash is {h1}")
        else:
            print(f"  CONTRACT BROKEN: {obj1!r} == {obj2!r} but hash({obj1!r})={h1} != hash({obj2!r})={h2}")


class CorrectPoint:
    """__hash__ and __eq__ use the same fields — contract satisfied."""
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CorrectPoint):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"CorrectPoint({self.x}, {self.y})"


class BrokenPoint:
    """
    __eq__ compares fields but __hash__ uses id() — contract violated.
    Two equal BrokenPoints have different hashes.
    This is a silent bug: the dict will store them as SEPARATE keys
    even though they compare equal.
    """
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BrokenPoint):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return id(self)   # WRONG: same point → same equality but different hash

    def __repr__(self) -> str:
        return f"BrokenPoint({self.x}, {self.y})"


def exercise_4_hash_contract() -> None:
    """Demonstrate correct vs broken hash contract implementations."""
    print("\n=== Exercise 4: Hash Contract Compliance ===\n")

    # Correct: built-in types
    print("Built-in types:")
    check_hash_contract(1, 1.0)        # int and float: 1 == 1.0 and same hash
    check_hash_contract("x", "x")

    # Correct: our CorrectPoint
    print("\nCorrectPoint (correct __hash__):")
    p1 = CorrectPoint(1.0, 2.0)
    p2 = CorrectPoint(1.0, 2.0)
    check_hash_contract(p1, p2)

    # Correct points work as dict keys and in sets
    point_map = {p1: "origin area"}
    print(f"  point_map[p2]: {point_map[p2]}  (p2 == p1, same hash → same slot)")
    print(f"  len({{p1, p2}}): {len({p1, p2})}  (de-duplicated correctly)")

    # Broken: BrokenPoint — equal objects, different hashes
    print("\nBrokenPoint (broken __hash__ uses id()):")
    b1 = BrokenPoint(1.0, 2.0)
    b2 = BrokenPoint(1.0, 2.0)
    check_hash_contract(b1, b2)

    # Silent bug: dict treats b1 and b2 as DIFFERENT keys
    broken_map: dict[BrokenPoint, str] = {b1: "from b1", b2: "from b2"}
    print(f"  dict has {len(broken_map)} entries (should be 1 — SILENT BUG!)")
    print(f"  {{b1, b2}} has {len({b1, b2})} elements (should be 1 — SILENT BUG!)")

    # Unhashable types
    print("\nUnhashable types:")
    print(f"  is_hashable([1,2,3]): {is_hashable([1, 2, 3])}")
    print(f"  is_hashable((1,2,3)): {is_hashable((1, 2, 3))}")
    print(f"  is_hashable((1,[2])): {is_hashable((1, [2]))}")  # tuple with list inside!


# =============================================================================
# EXERCISE 5: Word Occurrence Indexer — get() vs setdefault() vs defaultdict
# =============================================================================
#
# Ramalho uses this exact use case (Examples 3-4, 3-5, 3-6) to show three
# approaches to the same problem. Here we implement all three and compare
# them side by side, then measure the lookup count difference.


def build_index_naive(text: str) -> dict[str, list[tuple[int, int]]]:
    """
    dict.get() approach — two lookups per word (get + assign).
    This is what Ramalho calls "ugly" in Example 3-4.
    """
    index: dict[str, list[tuple[int, int]]] = {}
    for line_no, line in enumerate(text.splitlines(), 1):
        for col_no, word in enumerate(line.split(), 1):
            word = word.strip(".,!?;:")
            occurrences = index.get(word, [])     # lookup 1
            occurrences.append((line_no, col_no))
            index[word] = occurrences             # lookup 2 (re-insert)
    return index


def build_index_setdefault(text: str) -> dict[str, list[tuple[int, int]]]:
    """
    setdefault() approach — ONE lookup per word.
    Ramalho's Example 3-5: cleaner and faster.
    """
    index: dict[str, list[tuple[int, int]]] = {}
    for line_no, line in enumerate(text.splitlines(), 1):
        for col_no, word in enumerate(line.split(), 1):
            word = word.strip(".,!?;:")
            index.setdefault(word, []).append((line_no, col_no))
    return index


def build_index_defaultdict(text: str) -> dict[str, list[tuple[int, int]]]:
    """
    defaultdict(list) approach — no check at all.
    Ramalho's Example 3-6: simplest once you understand defaultdict.
    """
    index: defaultdict[str, list[tuple[int, int]]] = defaultdict(list)
    for line_no, line in enumerate(text.splitlines(), 1):
        for col_no, word in enumerate(line.split(), 1):
            word = word.strip(".,!?;:")
            index[word].append((line_no, col_no))
    return dict(index)


def exercise_5_word_indexer() -> None:
    """Build a word→occurrences index three ways and compare."""
    print("\n=== Exercise 5: Word Occurrence Indexer (Three Approaches) ===\n")

    text = """\
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated."""

    idx_naive = build_index_naive(text)
    idx_setdef = build_index_setdefault(text)
    idx_dd = build_index_defaultdict(text)

    # All three should produce identical results
    assert idx_naive == idx_setdef == idx_dd, "Results diverged!"
    print("All three approaches produce identical indices: OK\n")

    print("Word occurrences for 'better':")
    for loc in idx_setdef["better"]:
        print(f"  line {loc[0]}, col {loc[1]}")

    print("\nWord occurrences for 'is':")
    for loc in idx_setdef["is"]:
        print(f"  line {loc[0]}, col {loc[1]}")

    print("""
Approach comparison:
  get() + assign:    2 lookups per insert (get → append → re-assign)
  setdefault():      1 lookup per insert (get-or-create + return ref)
  defaultdict(list): 0 explicit checks (auto-creates on first access)

Rule of thumb:
  Use setdefault() when building nested structures in a plain dict.
  Use defaultdict(list) when EVERY missing key should produce an empty list.
  The difference matters when you want to check without creating:
    defaultdict: dd.get("missing") → None (no side effect)
    dd["missing"] → creates [] as side effect
""")


# =============================================================================
# EXERCISE 6: Set Algebra for Data Reconciliation
# =============================================================================
#
# Ramalho's Example 3-12 shows how set intersection replaces a nested loop.
# "Smart use of set operations can reduce both the line count and execution time."
#
# This exercise applies set algebra to a realistic data reconciliation problem:
# given two lists of user records from different systems, find who's in both,
# who's only in the old system (to deactivate), and who's only in the new
# system (to onboard).


def reconcile_users(
    old_system: list[str],
    new_system: list[str],
) -> dict[str, set[str]]:
    """
    Reconcile user lists from two systems using set operations.

    Returns a dict with three keys:
    - 'keep':       users in both systems (no action needed)
    - 'deactivate': users only in old system (need to remove)
    - 'onboard':    users only in new system (need to add)

    This replaces three nested loops + conditionals with three set expressions.
    """
    old = set(old_system)
    new = set(new_system)
    return {
        "keep":       old & new,     # intersection
        "deactivate": old - new,     # difference: old but not new
        "onboard":    new - old,     # difference: new but not old
    }


def exercise_6_set_reconciliation() -> None:
    """Demonstrate set algebra replacing nested loop logic."""
    print("\n=== Exercise 6: Set Algebra for User Reconciliation ===\n")

    old_users = ["alice", "bob", "charlie", "diana", "eve"]
    new_users = ["alice", "charlie", "eve", "frank", "grace"]

    result = reconcile_users(old_users, new_users)

    print(f"Old system:  {sorted(old_users)}")
    print(f"New system:  {sorted(new_users)}")
    print()
    print(f"Keep (both):        {sorted(result['keep'])}")
    print(f"Deactivate (old only): {sorted(result['deactivate'])}")
    print(f"Onboard (new only): {sorted(result['onboard'])}")

    # Verify: all users accounted for, no overlaps between result sets
    all_handled = result["keep"] | result["deactivate"] | result["onboard"]
    expected = set(old_users) | set(new_users)
    assert all_handled == expected, "Some users lost!"
    assert result["keep"].isdisjoint(result["deactivate"])
    assert result["keep"].isdisjoint(result["onboard"])
    assert result["deactivate"].isdisjoint(result["onboard"])
    print("\nVerification: all users accounted for, no overlaps — OK")

    print("""
The imperative equivalent would be three separate loops with conditionals.
Set operations express the intent directly: "users in both", "users only in A".
Beyond clarity, set membership is O(1), so the intersection scales to millions
of users with the same simple expression.
""")


# =============================================================================
# EXERCISE 7: Small Benchmark — dict lookup vs list scan
# =============================================================================
#
# Ramalho mentions: "Set membership testing is very efficient... A set may have
# millions of elements, but an element can be located directly by computing its
# hash code."
#
# This exercise measures it concretely on small-to-medium sizes.
# NOT a production benchmark — just enough to see the curve.


def exercise_7_lookup_benchmark() -> None:
    """
    Compare dict/set O(1) lookup against list O(n) scan across different sizes.
    Uses timeit for fair measurement.
    """
    import timeit

    print("\n=== Exercise 7: dict vs list Lookup (small benchmark) ===\n")

    sizes = [100, 1_000, 10_000, 100_000]
    print(f"{'Size':>10}  {'list (µs)':>12}  {'set (µs)':>12}  {'speedup':>10}")
    print("-" * 50)

    for n in sizes:
        data = list(range(n))
        as_list = data
        as_set = set(data)
        # Search for the LAST element (worst case for list)
        target = n - 1

        list_time = timeit.timeit(lambda: target in as_list, number=10_000) / 10_000
        set_time = timeit.timeit(lambda: target in as_set, number=10_000) / 10_000

        speedup = list_time / set_time if set_time > 0 else float("inf")
        print(
            f"{n:>10,}  {list_time * 1e6:>12.2f}  {set_time * 1e6:>12.2f}  {speedup:>9.1f}x"
        )

    print("""
Interpretation:
  list 'in': scans from start, O(n) — doubles with each 10x size increase.
  set 'in':  computes hash, one slot lookup, O(1) — nearly flat across sizes.

  The speedup is dramatic at large n because the list time grows linearly
  while the set time stays approximately constant.

  This is why you should NEVER use a list for membership tests in a hot loop.
  Convert to a set first if you'll do more than ~3 lookups.
""")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    exercise_1_str_key_dict()
    exercise_2_pattern_matching()
    exercise_3_layered_config()
    exercise_4_hash_contract()
    exercise_5_word_indexer()
    exercise_6_set_reconciliation()
    exercise_7_lookup_benchmark()
