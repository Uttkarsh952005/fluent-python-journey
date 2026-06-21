"""
Chapter 5: Benchmarks — Data Class Builders
=============================================
Measuring the real performance and memory characteristics of all three builders.

Benchmarks:
  1. Instantiation speed: namedtuple vs NamedTuple vs @dataclass vs plain class
  2. Memory footprint: tuple-backed vs dict-backed instances
  3. Attribute access: tuple indexing vs __dict__ lookup
  4. Equality check overhead: tuple comparison vs __eq__ logic
  5. asdict() vs _asdict() serialization speed
  6. frozen dataclass vs mutable + manual freeze

Run with: python benchmarks.py
"""

from __future__ import annotations

import sys
import timeit
import tracemalloc
from collections import namedtuple
from dataclasses import dataclass, field, asdict
from typing import NamedTuple

sys.stdout.reconfigure(encoding="utf-8")

N = 300_000


def section(title: str) -> None:
    print(f"\n{'=' * 62}")
    print(f"  {title}")
    print(f"{'=' * 62}")


def row(label: str, ns: float, note: str = "") -> None:
    note_str = f"  ← {note}" if note else ""
    print(f"  {label:<45} {ns:>8.1f} ns/op{note_str}")


def measure(stmt: str, setup: str, n: int = N) -> float:
    t = timeit.timeit(stmt=stmt, setup=setup, number=n)
    return (t / n) * 1_000_000_000


# ─────────────────────────────────────────────────────────────────────────────
# Setup — define all classes once
# ─────────────────────────────────────────────────────────────────────────────

# namedtuple
CityNT = namedtuple("CityNT", "name country population lat lon")

# NamedTuple
class CityTyped(NamedTuple):
    name: str
    country: str
    population: float
    lat: float
    lon: float

# @dataclass (mutable)
@dataclass
class CityDC:
    name: str
    country: str
    population: float
    lat: float
    lon: float

# @dataclass (frozen)
@dataclass(frozen=True)
class CityFrozen:
    name: str
    country: str
    population: float
    lat: float
    lon: float

# plain class — worst case baseline
class CityPlain:
    def __init__(self, name, country, population, lat, lon):
        self.name = name
        self.country = country
        self.population = population
        self.lat = lat
        self.lon = lon

ARGS = '"Tokyo", "JP", 37.4, 35.6895, 139.6917'
SETUP_NT     = f"from __main__ import CityNT"
SETUP_TYPED  = f"from __main__ import CityTyped"
SETUP_DC     = f"from __main__ import CityDC"
SETUP_FROZEN = f"from __main__ import CityFrozen"
SETUP_PLAIN  = f"from __main__ import CityPlain"


# =============================================================================
# Benchmark 1: Instantiation speed
# =============================================================================

section("Benchmark 1: Instantiation Speed")
print("  (Time to create one instance — lower is better)\n")

results_inst = {
    "namedtuple":      measure(f"CityNT({ARGS})", SETUP_NT),
    "NamedTuple":      measure(f"CityTyped({ARGS})", SETUP_TYPED),
    "@dataclass":      measure(f"CityDC({ARGS})", SETUP_DC),
    "@dataclass(frozen)": measure(f"CityFrozen({ARGS})", SETUP_FROZEN),
    "plain class":     measure(f"CityPlain({ARGS})", SETUP_PLAIN),
}

fastest = min(results_inst.values())
for label, ns in results_inst.items():
    ratio = ns / fastest
    row(label, ns, f"{ratio:.1f}x baseline" if ratio > 1.05 else "fastest")


# =============================================================================
# Benchmark 2: Memory footprint
# =============================================================================

section("Benchmark 2: Memory Footprint — 100,000 instances")
print("  (Tuple-backed classes use no __dict__ — much more compact)\n")

import sys as _sys

def measure_memory(factory, args: tuple) -> tuple[int, int]:
    """Returns (per_object_bytes, total_for_100k_bytes)."""
    tracemalloc.start()
    instances = [factory(*args) for _ in range(100_000)]
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    size_one = _sys.getsizeof(instances[0])
    return size_one, peak

args = ("Tokyo", "JP", 37.4, 35.6895, 139.6917)

print(f"  {'Type':<25} {'getsizeof':>12} {'100k peak KB':>14} {'notes'}")
print("  " + "-" * 65)

for label, factory in [
    ("namedtuple",         CityNT),
    ("NamedTuple",         CityTyped),
    ("@dataclass",         CityDC),
    ("@dataclass(frozen)", CityFrozen),
    ("plain class",        CityPlain),
]:
    size_one, peak = measure_memory(factory, args)
    print(f"  {label:<25} {size_one:>12} {peak / 1024:>14.1f} KB")

print("""
  Tuple-backed (namedtuple / NamedTuple):
    No __dict__ — fields stored directly in tuple slots.
    getsizeof ≈ 72 bytes for 5 fields (tuple overhead + 5 pointers).

  Dict-backed (@dataclass / plain class):
    Instance has __dict__ — separate dict allocation per object.
    getsizeof reports only the instance shell (~48 bytes),
    but __dict__ adds ~200+ bytes per instance.

  For large collections of records: use namedtuple or NamedTuple.
  For a few mutable objects: @dataclass overhead is acceptable.
""")


# =============================================================================
# Benchmark 3: Attribute Access
# =============================================================================

section("Benchmark 3: Attribute Access Speed")
print("  (Named access vs tuple index vs __dict__ lookup)\n")

city_nt    = CityNT("Tokyo", "JP", 37.4, 35.6895, 139.6917)
city_dc    = CityDC("Tokyo", "JP", 37.4, 35.6895, 139.6917)

# Named attribute access
t_nt_name  = measure("city_nt.population",  "from __main__ import city_nt")
t_dc_name  = measure("city_dc.population",  "from __main__ import city_dc")

# Tuple index access (namedtuple only)
t_nt_idx   = measure("city_nt[2]",           "from __main__ import city_nt")

row("namedtuple.population (named)",    t_nt_name)
row("namedtuple[2]         (index)",    t_nt_idx,  "index is slightly faster")
row("@dataclass.population (named)",    t_dc_name)

print("""
  namedtuple attribute access uses tuple __getitem__ under the hood.
  @dataclass attribute access goes through __dict__.
  Both are effectively O(1) — the difference is negligible in practice.
""")


# =============================================================================
# Benchmark 4: Equality Comparison
# =============================================================================

section("Benchmark 4: Equality Comparison")
print("  (Tuple comparison vs @dataclass __eq__)\n")

a_nt = CityNT("Tokyo", "JP", 37.4, 35.6895, 139.6917)
b_nt = CityNT("Tokyo", "JP", 37.4, 35.6895, 139.6917)
a_dc = CityDC("Tokyo", "JP", 37.4, 35.6895, 139.6917)
b_dc = CityDC("Tokyo", "JP", 37.4, 35.6895, 139.6917)

t_nt_eq = measure("a_nt == b_nt", "from __main__ import a_nt, b_nt")
t_dc_eq = measure("a_dc == b_dc", "from __main__ import a_dc, b_dc")

row("namedtuple equality  (a == b)", t_nt_eq, "uses tuple.__eq__ (C level)")
row("@dataclass equality  (a == b)", t_dc_eq, "uses generated __eq__ (Python level)")

ratio = t_dc_eq / t_nt_eq if t_nt_eq > 0 else 0
print(f"\n  -> namedtuple equality is {ratio:.1f}x faster (tuple comparison is C-level)")
print("""
  Tuple comparison iterates elements at C speed.
  @dataclass __eq__ calls Python-level field comparisons.
  For sorting/hashing millions of records: tuple types win.
""")


# =============================================================================
# Benchmark 5: Serialization — asdict() vs _asdict()
# =============================================================================

section("Benchmark 5: Serialization Speed")
print("  (asdict() for @dataclass vs _asdict() for namedtuple)\n")

city_nt2   = CityNT("Tokyo", "JP", 37.4, 35.6895, 139.6917)
city_dc2   = CityDC("Tokyo", "JP", 37.4, 35.6895, 139.6917)

t_nt_dict  = measure("city_nt2._asdict()", "from __main__ import city_nt2")
t_dc_dict  = measure("from dataclasses import asdict; asdict(city_dc2)",
                     "from __main__ import city_dc2; from dataclasses import asdict")

row("namedtuple._asdict()",    t_nt_dict)
row("dataclasses.asdict(dc)",  t_dc_dict,
    "deep copy — recursively converts nested dataclasses too")

print("""
  _asdict() is fast — namedtuple already has field names stored.
  asdict() is slower — recursively deep-converts all nested dataclasses/dicts.
  For flat objects: _asdict() wins.
  For nested hierarchies: asdict() is necessary and worth the cost.
""")


# =============================================================================
# Benchmark 6: frozen dataclass hashing
# =============================================================================

section("Benchmark 6: Hashing — frozen @dataclass vs namedtuple")
print("  (Can these be used as dict keys / set members?)\n")

frozen = CityFrozen("Tokyo", "JP", 37.4, 35.6895, 139.6917)
nt3    = CityNT("Tokyo", "JP", 37.4, 35.6895, 139.6917)

t_nt_hash     = measure("hash(nt3)",    "from __main__ import nt3")
t_frozen_hash = measure("hash(frozen)", "from __main__ import frozen")

row("hash(namedtuple)",          t_nt_hash,     "inherited from tuple")
row("hash(frozen @dataclass)",   t_frozen_hash, "generated __hash__ in Python")

print()
# Verify mutable @dataclass is NOT hashable
try:
    hash(city_dc)
except TypeError as e:
    print(f"  hash(mutable @dataclass): TypeError: {e}")

print("""
  namedtuple: hashable by default (it's a tuple).
  @dataclass(frozen=True): hashable — generates __hash__.
  @dataclass (mutable): NOT hashable by default (__hash__ = None).

  Rule: if you need dict keys or set membership → use namedtuple/NamedTuple
        or @dataclass(frozen=True, eq=True).
""")


# =============================================================================
# Summary
# =============================================================================

section("Summary — When to Use Which")
print("""
  PERFORMANCE SUMMARY:
  ┌─────────────────────┬──────────┬─────────┬────────────┬───────────┐
  │ Operation           │ ntuple   │ NTuple  │ @dataclass │ frozen DC │
  ├─────────────────────┼──────────┼─────────┼────────────┼───────────┤
  │ Instantiation       │ fastest  │ fast    │ moderate   │ slower    │
  │ Memory (N objects)  │ minimal  │ minimal │ higher     │ higher    │
  │ Attribute access    │ fast     │ fast    │ fast       │ fast      │
  │ Equality            │ fastest  │ fastest │ fast       │ fast      │
  │ Mutation            │ ✗ No     │ ✗ No    │ ✓ Yes      │ ✗ No      │
  │ Hashable            │ ✓ Yes    │ ✓ Yes   │ ✗ No       │ ✓ Yes     │
  │ Methods             │ hack     │ ✓ Yes   │ ✓ Yes      │ ✓ Yes     │
  │ Type annotations    │ ✗ No     │ ✓ Yes   │ ✓ Yes      │ ✓ Yes     │
  └─────────────────────┴──────────┴─────────┴────────────┴───────────┘

  DECISION GUIDE:
    Large read-only record collections → namedtuple (minimum memory)
    Value objects with type hints + methods → NamedTuple
    Mutable entities with business logic → @dataclass
    Immutable value type + dict/set key → @dataclass(frozen=True)
""")
