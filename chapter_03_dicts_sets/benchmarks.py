"""
Chapter 3: Benchmarks — Dicts and Sets Performance
====================================================
Measuring real hash table behavior: dict vs list lookup, set membership,
hash collision impact, and memory overhead.

Run with: python benchmarks.py

Benchmarks:
  1. dict lookup vs list scan — O(1) vs O(n)
  2. set membership vs list membership — across sizes
  3. set literal {1,2,3} vs set([1,2,3]) constructor — bytecode difference
  4. dict construction methods — which is fastest?
  5. tracemalloc: dict vs list memory overhead for the same data
  6. defaultdict vs setdefault — insertion overhead
"""

from __future__ import annotations

import sys
import timeit
import tracemalloc
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

NUMBER = 500_000


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def section(title: str) -> None:
    print(f"\n{'=' * 62}")
    print(f"  {title}")
    print(f"{'=' * 62}")


def row(label: str, ns: float) -> None:
    print(f"  {label:<48} {ns:>8.1f} ns/op")


def measure(stmt: str, setup: str = "", n: int = NUMBER) -> float:
    elapsed = timeit.timeit(stmt=stmt, setup=setup, number=n, globals=globals())
    return (elapsed / n) * 1e9


# ─────────────────────────────────────────────────────────────────────────────
# Setup data
# ─────────────────────────────────────────────────────────────────────────────

N = 10_000
keys = [f"key_{i}" for i in range(N)]
values = list(range(N))

as_dict = dict(zip(keys, values))
as_list_of_pairs = list(zip(keys, values))
as_set = set(keys)
as_list = list(keys)

TARGET_KEY = f"key_{N - 1}"    # worst case for list scan (last element)
TARGET_MISSING = "key_MISSING"  # not in either — full scan for list


# =============================================================================
# Benchmark 1: dict lookup vs list scan (string keys)
# =============================================================================

section("Benchmark 1: dict lookup vs list scan — O(1) vs O(n)")
print(f"  Dataset: {N:,} string keys, searching for last key (worst case for list)\n")

t_dict_hit   = measure("TARGET_KEY in as_dict")
t_dict_miss  = measure("TARGET_MISSING in as_dict")
t_list_hit   = measure("TARGET_KEY in as_list", n=10_000)
t_list_miss  = measure("TARGET_MISSING in as_list", n=10_000)

row("dict — key present (hash hit)",        t_dict_hit)
row("dict — key missing (hash miss)",       t_dict_miss)
row("list — key present (scan to end)",     t_list_hit)
row("list — key missing (full scan)",       t_list_miss)

print(f"\n  -> dict is {t_list_hit / t_dict_hit:.0f}x faster than list (hit)")
print(f"  -> dict is {t_list_miss / t_dict_miss:.0f}x faster than list (miss)")
print("""
  Why: dict computes hash(key) → derives slot index → checks one entry.
  List must iterate from index 0, comparing each element until found.
  At N=10,000, the list scans an average of 5,000 elements per hit.
  At N=100,000, list is ~10x slower still. Dict stays flat.
""")


# =============================================================================
# Benchmark 2: set membership vs list membership — across sizes
# =============================================================================

section("Benchmark 2: set vs list membership across sizes")
print(f"  {'Size':>10}  {'list (µs)':>12}  {'set (µs)':>12}  {'speedup':>10}")
print("  " + "-" * 48)

for n in [100, 1_000, 10_000, 100_000]:
    data = list(range(n))
    lst  = data
    st   = set(data)
    target = n - 1  # worst case for list

    t_lst = timeit.timeit(lambda: target in lst, number=50_000) / 50_000
    t_set = timeit.timeit(lambda: target in st,  number=50_000) / 50_000
    speedup = t_lst / t_set

    print(f"  {n:>10,}  {t_lst * 1e6:>12.3f}  {t_set * 1e6:>12.3f}  {speedup:>9.1f}x")

print("""
  Interpretation:
    list: time grows linearly with n (O(n) scan).
    set:  time stays approximately constant (O(1) hash lookup).
    At n=100,000 the gap is enormous — never use a list for repeated membership.
""")


# =============================================================================
# Benchmark 3: set literal vs set() constructor
# =============================================================================

section("Benchmark 3: set literal {1,2,3} vs set([1,2,3]) constructor")
print("  (Ramalho mentions this: literal uses BUILD_SET bytecode)\n")

t_literal = measure("{1, 2, 3, 4, 5}")
t_constructor = measure("set([1, 2, 3, 4, 5])")

row("set literal:      {1, 2, 3, 4, 5}", t_literal)
row("set() call:  set([1, 2, 3, 4, 5])", t_constructor)

print(f"\n  -> set literal is {t_constructor / t_literal:.1f}x faster")
print("""  Why: The literal compiles to a single BUILD_SET bytecode instruction.
  set([...]) requires: LOAD_GLOBAL 'set' + BUILD_LIST + CALL.
  For large or hot code paths, prefer literals when elements are static.
""")


# =============================================================================
# Benchmark 4: dict construction methods
# =============================================================================

section("Benchmark 4: dict construction methods")
print("  (Which is the fastest way to build a small dict?)\n")

t_literal  = measure("{'a': 1, 'b': 2, 'c': 3}")
t_kwargs   = measure("dict(a=1, b=2, c=3)")
t_zip      = measure("dict(zip(('a','b','c'), (1,2,3)))")
t_fromkeys = measure("dict.fromkeys(('a','b','c'), 0)")

row("dict literal:   {'a':1,'b':2,'c':3}", t_literal)
row("dict() kwargs:  dict(a=1,b=2,c=3)",   t_kwargs)
row("dict(zip()):    dict(zip(k,v))",       t_zip)
row("dict.fromkeys(): dict.fromkeys(k,0)",  t_fromkeys)

fastest = min(t_literal, t_kwargs, t_zip, t_fromkeys)
print(f"""
  -> literal is the baseline
  Relative: kwargs={t_kwargs/t_literal:.1f}x, zip={t_zip/t_literal:.1f}x, fromkeys={t_fromkeys/t_literal:.1f}x

  Rule of thumb:
    Use literal when keys are known at write-time (fastest, most readable).
    Use dict() kwargs when constructing from variables with string keys.
    Use dict(zip()) or dict comprehension when building from sequences.
""")


# =============================================================================
# Benchmark 5: Memory — dict vs list vs set
# =============================================================================

section("Benchmark 5: Memory overhead — dict vs list vs set (tracemalloc)")
print("  (How much memory does each structure use for N integer elements?)\n")

print(f"  {'Structure':>20}  {'N':>8}  {'Memory (KB)':>12}  {'Bytes/item':>12}")
print("  " + "-" * 58)

for n in [1_000, 10_000, 100_000]:
    # dict: int → int
    tracemalloc.start()
    d = {i: i for i in range(n)}
    _, peak_dict = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del d

    # list of ints
    tracemalloc.start()
    lst = list(range(n))
    _, peak_list = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del lst

    # set of ints
    tracemalloc.start()
    s = set(range(n))
    _, peak_set = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del s

    print(f"  {'dict {i:i}':>20}  {n:>8,}  {peak_dict/1024:>12.1f}  {peak_dict/n:>12.1f}")
    print(f"  {'list [i]':>20}  {n:>8,}  {peak_list/1024:>12.1f}  {peak_list/n:>12.1f}")
    print(f"  {'set {i}':>20}  {n:>8,}  {peak_set/1024:>12.1f}  {peak_set/n:>12.1f}")
    print()

print("""  Why dict uses more memory than list:
    - dict allocates a sparse index table (1/3+ of slots kept empty)
    - each entry stores: hash, key pointer, value pointer
    - list stores only pointers, no hash overhead
    - set is between: hash table without values
  This is the memory/speed tradeoff: pay extra bytes to get O(1) lookup.
""")


# =============================================================================
# Benchmark 6: defaultdict vs setdefault — which is faster for building index?
# =============================================================================

section("Benchmark 6: defaultdict(list) vs setdefault for index building")
print("  (Both solve the same problem — which has less overhead?)\n")

WORDS = ["apple", "banana", "cherry", "apple", "date", "banana", "elderberry"] * 200


def build_with_setdefault(words: list[str]) -> dict[str, list[int]]:
    index: dict[str, list[int]] = {}
    for i, word in enumerate(words):
        index.setdefault(word, []).append(i)
    return index


def build_with_defaultdict(words: list[str]) -> dict[str, list[int]]:
    index: defaultdict[str, list[int]] = defaultdict(list)
    for i, word in enumerate(words):
        index[word].append(i)
    return dict(index)


t_sd = measure("build_with_setdefault(WORDS)", n=5_000)
t_dd = measure("build_with_defaultdict(WORDS)", n=5_000)

row("setdefault approach", t_sd)
row("defaultdict approach", t_dd)

winner = "defaultdict" if t_dd < t_sd else "setdefault"
ratio = max(t_sd, t_dd) / min(t_sd, t_dd)
print(f"\n  -> {winner} is {ratio:.1f}x faster")
print("""
  Why defaultdict wins: it avoids the overhead of the Python-level
  setdefault() method call. The default_factory call is cheaper because
  defaultdict's __missing__ is implemented in C.

  Practical rule: use defaultdict(list) for building inverted indexes.
  Use setdefault() when working with plain dicts you don't own.
""")


# =============================================================================
# Summary
# =============================================================================

section("Summary — Key Numbers to Remember")
print("""
  dict/set O(1) lookup:       ~40–80 ns  (hash + one memory access)
  list O(n) scan (10k items): ~200–500 µs (growing linearly with n)
  dict memory overhead:       ~3–4x more than equivalent list
  set memory overhead:        ~2–3x more than equivalent list

  Rules:
    1. Any repeated membership test → use a set or dict, never a list
    2. Building inverted indexes → defaultdict(list) over setdefault
    3. Set literal {x,y,z} → faster than set([x,y,z]) due to BUILD_SET opcode
    4. dict literal {'k':v} → fastest construction for static keys
    5. Memory-sensitive code → dict has significant overhead vs list/array
""")
