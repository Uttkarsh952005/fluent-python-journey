"""
Chapter 5: Data Class Builders — Examples
==========================================
Comparative exploration of Python's three data class builders:
  namedtuple / typing.NamedTuple / @dataclass

Topics:
  Part 1  -- The boilerplate problem: plain class vs all three builders
  Part 2  -- collections.namedtuple: factory, _fields, _asdict, _replace
  Part 3  -- typing.NamedTuple: typed fields, class syntax, methods
  Part 4  -- @dataclass: mutable, frozen, field(), order=True
  Part 5  -- field() options: default_factory, repr, compare, hash
  Part 6  -- __post_init__: validation and computed fields
  Part 7  -- ClassVar and InitVar — class-level vs init-only attributes

Run with: python examples.py
"""

from __future__ import annotations

import sys
from collections import namedtuple
from dataclasses import dataclass, field, fields, asdict, replace, InitVar
from datetime import date
from enum import Enum, auto
from typing import ClassVar, NamedTuple, Optional

sys.stdout.reconfigure(encoding="utf-8")


# =============================================================================
# PART 1: The Boilerplate Problem
# =============================================================================


def boilerplate_problem_demo() -> None:
    """
    Without data class builders, a simple record class requires writing
    __init__, __repr__, __eq__ by hand — and missing them causes silent bugs.
    """
    print("=== Part 1: The Boilerplate Problem ===\n")

    class PlainCoordinate:
        """No boilerplate helpers — raw Python class."""
        def __init__(self, lat: float, lon: float) -> None:
            self.lat = lat
            self.lon = lon

    moscow = PlainCoordinate(55.76, 37.62)

    print("PlainCoordinate (no builder):")
    print(f"  repr:      {moscow}")          # <__main__.PlainCoordinate object at 0x...>
    print(f"  lat:       {moscow.lat}")
    equal = moscow == PlainCoordinate(55.76, 37.62)
    print(f"  equality:  {equal}")           # False! compares object identity, not values
    print("  ← repr is useless, equality is WRONG (uses id() not values)\n")

    # Now the same class with namedtuple — three builders, identical outcome
    NT   = namedtuple("Coordinate", "lat lon")
    p_nt = NT(55.76, 37.62)
    print(f"namedtuple:      repr={p_nt!r}  eq={p_nt == NT(55.76, 37.62)}")

    class NTTyped(NamedTuple):
        lat: float
        lon: float

    p_ntt = NTTyped(55.76, 37.62)
    print(f"NamedTuple:      repr={p_ntt!r}  eq={p_ntt == NTTyped(55.76, 37.62)}")

    @dataclass
    class DC:
        lat: float
        lon: float

    p_dc = DC(55.76, 37.62)
    print(f"@dataclass:      repr={p_dc!r}  eq={p_dc == DC(55.76, 37.62)}")

    print("\nAll three auto-generate __init__, __repr__, __eq__.")
    print("The boilerplate disappears. The intent is clear.\n")


# =============================================================================
# PART 2: collections.namedtuple
# =============================================================================


def namedtuple_demo() -> None:
    """
    collections.namedtuple: the original factory (Python 2.6+).

    Key facts:
    - Subclass of tuple — fully interchangeable with tuple
    - Immutable — no attribute assignment after creation
    - Zero memory overhead vs plain tuple (fields stored as tuple positions)
    - Methods: _fields, _asdict(), _make(), _replace()
    """
    print("=== Part 2: collections.namedtuple ===\n")

    # Classic factory syntax — two forms:
    City = namedtuple("City", "name country population coordinates")
    # Equivalent: namedtuple("City", ["name", "country", "population", "coordinates"])

    Coordinate = namedtuple("Coordinate", "lat lon", defaults=["WGS84"])
    # Wait — WGS84 is a reference system. Let me model this properly:
    Coordinate = namedtuple("Coordinate", "lat lon reference", defaults=["WGS84"])

    tokyo = City("Tokyo", "JP", 36.933, Coordinate(35.689722, 139.691667))
    delhi = City("Delhi NCR", "IN", 21.935, Coordinate(28.613889, 77.208889))

    print(f"tokyo: {tokyo}")
    print(f"delhi: {delhi}\n")

    # Key namedtuple API
    print(f"City._fields:  {City._fields}")
    print(f"tokyo[1]:      {tokyo[1]}  ← tuple indexing still works")
    print(f"tokyo.country: {tokyo.country}  ← named access\n")

    # _asdict() — returns a plain dict (since Python 3.8; was OrderedDict before)
    tokyo_dict = tokyo._asdict()
    print(f"._asdict():    {tokyo_dict}")
    print(f"type:          {type(tokyo_dict).__name__}\n")

    # _make() — construct from any iterable (great for reading CSV rows)
    raw_row = ("Mumbai", "IN", 20.667, Coordinate(19.076, 72.877))
    mumbai = City._make(raw_row)
    print(f"._make():      {mumbai}")

    # _replace() — returns a NEW tuple with substituted fields (immutable!)
    updated_tokyo = tokyo._replace(population=37.4)
    print(f"._replace():   {updated_tokyo}")
    print(f"original unchanged: {tokyo.population}\n")

    # defaults (Python 3.7+) — for rightmost N fields
    print(f"Coordinate(0, 0):           {Coordinate(0, 0)}")
    print(f"_field_defaults:            {Coordinate._field_defaults}\n")

    # issubclass check — it IS a tuple
    print(f"issubclass(City, tuple):    {issubclass(City, tuple)}")
    print(f"isinstance(tokyo, tuple):   {isinstance(tokyo, tuple)}")

    # Sorting works automatically (tuple comparison)
    cities = [tokyo, delhi, mumbai]
    sorted_by_pop = sorted(cities, key=lambda c: c.population)
    print(f"\nSorted by population: {[c.name for c in sorted_by_pop]}")


# =============================================================================
# PART 3: typing.NamedTuple
# =============================================================================


def typed_namedtuple_demo() -> None:
    """
    typing.NamedTuple: same as namedtuple but with type annotations.

    Key facts:
    - Class statement syntax — readable, supports docstrings and methods
    - NOT a subclass of typing.NamedTuple (it's a metaclass trick)
    - IS a subclass of tuple
    - Type hints are enforced by static checkers (Mypy), NOT at runtime
    """
    print("\n=== Part 3: typing.NamedTuple ===\n")

    class Coordinate(NamedTuple):
        """A geographic coordinate with optional datum reference."""
        lat: float
        lon: float
        reference: str = "WGS84"  # rightmost field has default

        def __str__(self) -> str:
            ns = "N" if self.lat >= 0 else "S"
            we = "E" if self.lon >= 0 else "W"
            return f"{abs(self.lat):.1f}°{ns}, {abs(self.lon):.1f}°{we}"

        def distance_to_equator(self) -> float:
            """Rough km distance to equator."""
            return abs(self.lat) * 111.32  # 1° latitude ≈ 111.32 km

    moscow = Coordinate(55.756, 37.617)
    sydney = Coordinate(-33.8688, 151.2093)

    print(f"moscow:          {moscow!r}")
    print(f"str(moscow):     {moscow}")
    print(f"sydney:          {sydney!r}")
    print(f"str(sydney):     {sydney}")

    print(f"\nmoscow._fields:  {moscow._fields}")
    print(f"__annotations__: {Coordinate.__annotations__}")
    print(f"issubclass of tuple:          {issubclass(Coordinate, tuple)}")
    print(f"issubclass of NamedTuple:     False  (NamedTuple is syntax, not a real base)")

    # Type hints have NO runtime effect
    print("\nType hints have NO runtime effect:")
    trash = Coordinate(lat="NOT A FLOAT", lon=None)  # type: ignore
    print(f"  Coordinate(lat='NOT A FLOAT', lon=None): {trash!r}")
    print("  No error! Type checking requires Mypy/Pyright, not the interpreter.\n")

    print(f"distance_to_equator: moscow={moscow.distance_to_equator():.0f}km")
    print(f"distance_to_equator: sydney={sydney.distance_to_equator():.0f}km")


# =============================================================================
# PART 4: @dataclass — mutable, frozen, order
# =============================================================================


def dataclass_basics_demo() -> None:
    """
    @dataclass: the most flexible builder (Python 3.7+).

    Default parameters:
      init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False

    Key difference from NamedTuple:
    - NOT a tuple subclass — regular class hierarchy
    - Mutable by default (can be frozen)
    - Supports order=True for comparison operators
    - No memory overhead from tuple structure
    """
    print("\n=== Part 4: @dataclass Basics ===\n")

    # Default: mutable
    @dataclass
    class Point:
        x: float
        y: float

    p = Point(1.0, 2.0)
    print(f"Point(1.0, 2.0): {p}")
    p.x = 99.0  # mutation works
    print(f"After p.x = 99: {p}\n")

    # frozen=True: immutable (raises FrozenInstanceError on mutation)
    @dataclass(frozen=True)
    class FrozenPoint:
        x: float
        y: float

    fp = FrozenPoint(1.0, 2.0)
    print(f"FrozenPoint(1.0, 2.0): {fp}")
    try:
        fp.x = 99.0  # type: ignore[misc]
    except Exception as e:
        print(f"FrozenPoint mutation: {type(e).__name__}: {e}\n")

    # frozen=True + eq=True → __hash__ is generated → hashable!
    d = {fp: "origin area"}
    print(f"Frozen dataclass as dict key: {d[fp]}")

    # order=True: generates __lt__, __le__, __gt__, __ge__
    @dataclass(order=True)
    class Student:
        grade: float
        name: str  # note: comparison is field ORDER (grade first, then name)

    students = [
        Student(3.8, "Alice"),
        Student(3.9, "Bob"),
        Student(3.8, "Charlie"),
    ]
    students.sort()  # sorts by grade first, then name
    print(f"\nSorted students (order=True):")
    for s in students:
        print(f"  {s}")

    # dataclasses.replace() — like ._replace() for namedtuple
    original = FrozenPoint(1.0, 2.0)
    modified = replace(original, x=5.0)
    print(f"\nreplace(FrozenPoint(1,2), x=5): {modified}")

    # dataclasses.asdict() — deep conversion to dict
    @dataclass
    class Address:
        street: str
        city: str

    @dataclass
    class Person:
        name: str
        address: Address

    person = Person("Alice", Address("123 Main St", "Springfield"))
    print(f"\nasdict(Person): {asdict(person)}")
    print("Note: nested dataclasses are recursively converted to dicts")


# =============================================================================
# PART 5: field() — Fine-grained field control
# =============================================================================


def field_options_demo() -> None:
    """
    The dataclasses.field() function provides per-field control:
    default         — simple default value (immutable only!)
    default_factory — callable that produces fresh default each time
    repr            — include/exclude from __repr__
    compare         — include/exclude from __eq__ and ordering
    hash            — include/exclude from __hash__
    init            — include/exclude from __init__
    metadata        — arbitrary user data dict (ignored by dataclass)
    """
    print("\n=== Part 5: field() Options ===\n")

    @dataclass
    class ClubMember:
        name: str
        guests: list[str]       = field(default_factory=list)
        athlete: bool           = field(default=False, repr=False)    # hidden from repr
        join_date: date | None  = field(default=None, compare=False)  # not compared

    alice = ClubMember("Alice")
    bob   = ClubMember("Bob", guests=["Carol", "Dave"], athlete=True)
    alice2 = ClubMember("Alice", join_date=date(2024, 1, 1))  # different date

    print(f"alice:  {alice}")
    print(f"bob:    {bob}")
    print(f"alice2: {alice2}")
    print(f"alice == alice2: {alice == alice2}  ← join_date excluded from compare!\n")

    # The mutable default trap — @dataclass prevents it at class definition time
    print("Mutable default trap:")
    try:
        @dataclass
        class Broken:
            items: list = []  # type: ignore  # ← will raise ValueError!
    except ValueError as e:
        print(f"  @dataclass raises ValueError: {e}")
    print("  Use field(default_factory=list) instead\n")

    # metadata — arbitrary user data on the field (ignored by @dataclass)
    @dataclass
    class Product:
        name: str
        price: float = field(metadata={"unit": "USD", "precision": 2})

    price_field = next(f for f in fields(Product) if f.name == "price")
    print(f"price field metadata: {price_field.metadata}")


# =============================================================================
# PART 6: __post_init__ — Validation and Computed Fields
# =============================================================================


def post_init_demo() -> None:
    """
    __post_init__ runs after the generated __init__.
    Used for:
    - Field validation (raise ValueError for invalid data)
    - Computed fields (derive one field from others)
    - Side effects (register instance in a class-level registry)
    """
    print("\n=== Part 6: __post_init__ ===\n")

    @dataclass
    class ClubMember:
        name: str
        guests: list[str] = field(default_factory=list)
        handle: str = ""

        # class attribute (NOT a field — no type annotation visible to @dataclass)
        all_handles: ClassVar[set[str]] = set()

        def __post_init__(self) -> None:
            cls = self.__class__
            if not self.handle:
                self.handle = self.name.split()[0]
            if self.handle in cls.all_handles:
                raise ValueError(f"handle {self.handle!r} already exists.")
            cls.all_handles.add(self.handle)

    leo = ClubMember("Leo Rochael")
    print(f"leo:     {leo}")

    try:
        leo2 = ClubMember("Leo DaVinci")  # auto-handle 'Leo' is taken
    except ValueError as e:
        print(f"Duplicate handle: {e}")

    leo2 = ClubMember("Leo DaVinci", handle="Neo")
    print(f"leo2:    {leo2}\n")

    # Computed fields — init=False means not in __init__, computed in __post_init__
    @dataclass
    class Circle:
        radius: float
        area: float = field(init=False, repr=True)

        def __post_init__(self) -> None:
            import math
            self.area = math.pi * self.radius ** 2

    c = Circle(radius=5.0)
    print(f"Circle(radius=5): {c}")
    print(f"area computed in __post_init__: {c.area:.4f}\n")

    # Validation with __post_init__
    @dataclass
    class TemperatureReading:
        celsius: float
        sensor_id: str

        def __post_init__(self) -> None:
            if self.celsius < -273.15:
                raise ValueError(
                    f"Temperature {self.celsius}°C is below absolute zero"
                )

    reading = TemperatureReading(celsius=22.5, sensor_id="SENSOR_A")
    print(f"Valid reading: {reading}")

    try:
        bad = TemperatureReading(celsius=-500.0, sensor_id="BAD")
    except ValueError as e:
        print(f"Invalid reading: {e}")


# =============================================================================
# PART 7: ClassVar and InitVar
# =============================================================================


def classvar_and_initvar_demo() -> None:
    """
    ClassVar[T]: marks a class attribute (not an instance field).
    @dataclass ignores ClassVar fields — they are NOT in __init__ or __repr__.

    InitVar[T]: marks an init-only argument.
    It appears in __init__ and is passed to __post_init__, but is NOT stored.
    """
    print("\n=== Part 7: ClassVar and InitVar ===\n")

    @dataclass
    class Tracker:
        """Demonstrates ClassVar — shared state across instances."""
        name: str
        # ClassVar: class-level counter, not an instance field
        _instance_count: ClassVar[int] = 0

        def __post_init__(self) -> None:
            Tracker._instance_count += 1

    t1 = Tracker("first")
    t2 = Tracker("second")
    t3 = Tracker("third")
    print(f"Instances created: {Tracker._instance_count}")
    print(f"t1 repr:           {t1}  ← no _instance_count in repr (it's ClassVar)")
    print(f"'_instance_count' in t1.__dict__: {'_instance_count' in t1.__dict__}\n")

    # InitVar: passed to __post_init__ but not stored as instance attribute
    @dataclass
    class Config:
        """Config loaded from a dict — dict is InitVar, not stored."""
        host: str
        port: int
        debug: bool = False
        # InitVar: init argument that feeds __post_init__ but is not a field
        config_dict: InitVar[dict[str, object] | None] = None

        def __post_init__(self, config_dict: dict[str, object] | None) -> None:
            if config_dict:
                self.host = str(config_dict.get("host", self.host))
                self.port = int(config_dict.get("port", self.port))  # type: ignore[arg-type]
                self.debug = bool(config_dict.get("debug", self.debug))

    c1 = Config(host="localhost", port=8080)
    c2 = Config(host="", port=0, config_dict={"host": "prod.example.com", "port": 443, "debug": False})

    print(f"c1: {c1}")
    print(f"c2: {c2}")
    print(f"'config_dict' in c2.__dict__: {'config_dict' in c2.__dict__}  ← not stored!\n")

    print("Field names via dataclasses.fields():")
    for f in fields(Config):
        print(f"  {f.name}: {f.type}")
    print("  (config_dict is InitVar — NOT listed here)")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    boilerplate_problem_demo()
    namedtuple_demo()
    typed_namedtuple_demo()
    dataclass_basics_demo()
    field_options_demo()
    post_init_demo()
    classvar_and_initvar_demo()
