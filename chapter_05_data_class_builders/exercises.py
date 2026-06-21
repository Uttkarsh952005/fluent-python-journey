"""
Chapter 5: Exercises — Data Class Builders
===========================================
Original exercises pushing at edge cases of namedtuple, NamedTuple, and @dataclass.

Run with: python exercises.py
"""

from __future__ import annotations

import sys
import json
from collections import namedtuple
from dataclasses import dataclass, field, fields, asdict, replace
from datetime import date, datetime
from enum import Enum, auto
from typing import ClassVar, NamedTuple

sys.stdout.reconfigure(encoding="utf-8")


# =============================================================================
# EXERCISE 1: Builder Comparison — Same Domain, Three Ways
# =============================================================================
#
# Model a book record three ways and compare the tradeoffs.
# This forces you to understand what each builder gives/costs.


def exercise_1_builder_comparison() -> None:
    print("=== Exercise 1: Builder Comparison — Book Record ===\n")

    # --- namedtuple: simplest, but no type hints, no methods without hacks ---
    BookNT = namedtuple("BookNT", "title author year pages", defaults=[0])

    # --- typing.NamedTuple: typed, class syntax, adds methods, still immutable ---
    class BookTyped(NamedTuple):
        title: str
        author: str
        year: int
        pages: int = 0

        def age(self) -> int:
            return datetime.now().year - self.year

        def is_classic(self) -> bool:
            return self.age() > 25

    # --- @dataclass: mutable by default, most flexible ---
    @dataclass
    class BookDC:
        title: str
        author: str
        year: int
        pages: int = 0
        tags: list[str] = field(default_factory=list)

        def age(self) -> int:
            return datetime.now().year - self.year

        def add_tag(self, tag: str) -> None:
            self.tags.append(tag)

    # Same data, three representations
    fluent_nt     = BookNT("Fluent Python", "Luciano Ramalho", 2022, 1012)
    fluent_typed  = BookTyped("Fluent Python", "Luciano Ramalho", 2022, 1012)
    fluent_dc     = BookDC("Fluent Python", "Luciano Ramalho", 2022, 1012)

    print("repr:")
    print(f"  namedtuple:  {fluent_nt!r}")
    print(f"  NamedTuple:  {fluent_typed!r}")
    print(f"  @dataclass:  {fluent_dc!r}\n")

    print("Structural differences:")
    print(f"  namedtuple is tuple:   {isinstance(fluent_nt, tuple)}")
    print(f"  NamedTuple is tuple:   {isinstance(fluent_typed, tuple)}")
    print(f"  @dataclass is tuple:   {isinstance(fluent_dc, tuple)}")
    print(f"  nt[0]:    {fluent_nt[0]}  ← tuple indexing works")
    print(f"  typed[0]: {fluent_typed[0]}  ← also works (it's a tuple)")
    print(f"  dc[0]:    ", end="")
    try:
        print(fluent_dc[0])
    except TypeError as e:
        print(f"TypeError: {e}\n")

    print("Mutability:")
    fluent_dc.tags.append("advanced")
    fluent_dc.pages = 1013  # mutable!
    print(f"  @dataclass mutated: pages={fluent_dc.pages}, tags={fluent_dc.tags}")

    try:
        fluent_typed._replace(pages=999)  # _replace returns NEW — original unchanged
        print(f"  NamedTuple _replace: creates new object, original pages={fluent_typed.pages}")
    except Exception as e:
        print(f"  {e}")

    print("\nMethod access:")
    print(f"  NamedTuple .age(): {fluent_typed.age()} years old")
    print(f"  NamedTuple .is_classic(): {fluent_typed.is_classic()}")
    print(f"  @dataclass .age(): {fluent_dc.age()} years old")

    print("""
Builder selection guide:
  namedtuple   → quick record, no type safety, compatible with tuple APIs
  NamedTuple   → typed record, immutable, needs methods → prefer this for value objects
  @dataclass   → mutable state, complex logic, validation → prefer for mutable entities
""")


# =============================================================================
# EXERCISE 2: __post_init__ Validation Pipeline
# =============================================================================
#
# Build a validated sensor reading using __post_init__ for domain rules.


class SensorType(Enum):
    TEMPERATURE = auto()
    HUMIDITY    = auto()
    PRESSURE    = auto()


VALID_RANGES: dict[SensorType, tuple[float, float]] = {
    SensorType.TEMPERATURE: (-50.0, 100.0),      # Celsius
    SensorType.HUMIDITY:    (0.0, 100.0),         # %
    SensorType.PRESSURE:    (800.0, 1100.0),      # hPa
}


@dataclass
class SensorReading:
    sensor_id: str
    sensor_type: SensorType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    quality: str = field(init=False)

    def __post_init__(self) -> None:
        # Validate sensor_id format
        if not self.sensor_id.startswith("SENSOR_"):
            raise ValueError(f"sensor_id must start with 'SENSOR_', got {self.sensor_id!r}")

        # Validate value range
        lo, hi = VALID_RANGES[self.sensor_type]
        if not (lo <= self.value <= hi):
            raise ValueError(
                f"{self.sensor_type.name} value {self.value} out of range [{lo}, {hi}]"
            )

        # Computed field — quality based on extremes
        mid = (lo + hi) / 2
        deviation = abs(self.value - mid) / (hi - lo)
        self.quality = "GOOD" if deviation < 0.4 else "MARGINAL"


def exercise_2_validated_dataclass() -> None:
    print("=== Exercise 2: Validated Sensor Reading (@post_init) ===\n")

    valid_readings = [
        ("SENSOR_A", SensorType.TEMPERATURE, 22.5),
        ("SENSOR_B", SensorType.HUMIDITY, 65.0),
        ("SENSOR_C", SensorType.PRESSURE, 1013.25),
    ]

    for sid, stype, val in valid_readings:
        r = SensorReading(sid, stype, val)
        print(f"  {r.sensor_id:<12} {r.sensor_type.name:<12} {r.value:>8}  quality={r.quality}")

    print()
    invalid = [
        ("BAD_ID",    SensorType.TEMPERATURE, 25.0, "bad sensor_id format"),
        ("SENSOR_D",  SensorType.TEMPERATURE, 200.0, "temperature out of range"),
        ("SENSOR_E",  SensorType.HUMIDITY, -10.0, "humidity out of range"),
    ]

    for sid, stype, val, desc in invalid:
        try:
            SensorReading(sid, stype, val)
        except ValueError as e:
            print(f"  [{desc}]: ValueError: {e}")


# =============================================================================
# EXERCISE 3: Immutable Value Object with NamedTuple
# =============================================================================
#
# Model money as an immutable value object. Arithmetic creates new instances.
# This is the canonical use case for NamedTuple — value objects in DDD.


class Money(NamedTuple):
    """
    Immutable money value object.
    Demonstrates NamedTuple as a proper value object:
    - identity is the VALUE, not the memory address
    - arithmetic produces new Money instances
    - hashable → can be used as dict key
    """
    amount: int      # stored in cents to avoid float imprecision
    currency: str = "USD"

    @classmethod
    def of(cls, dollars: float, currency: str = "USD") -> "Money":
        """Construct from floating-point dollars — converts to integer cents."""
        return cls(round(dollars * 100), currency)

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: float) -> "Money":
        return Money(round(self.amount * factor), self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount / 100:.2f}"

    def __repr__(self) -> str:
        return f"Money({self.amount / 100:.2f}, {self.currency!r})"


def exercise_3_money_value_object() -> None:
    print("\n=== Exercise 3: Money as Immutable NamedTuple Value Object ===\n")

    price   = Money.of(9.99)
    tax     = Money.of(0.80)
    total   = price + tax
    doubled = price * 2

    print(f"price:          {price}")
    print(f"tax:            {tax}")
    print(f"price + tax:    {total}")
    print(f"price * 2:      {doubled}")

    # Hashable — usable as dict key
    cart: dict[Money, str] = {price: "book", total: "book+tax"}
    print(f"\nAs dict key:    cart[price] = {cart[price]!r}")

    # Value equality — two Money objects with same amount/currency are equal
    m1 = Money.of(9.99)
    m2 = Money.of(9.99)
    print(f"\nm1 == m2: {m1 == m2}  (value equality — both are {m1})")
    print(f"m1 is m2: {m1 is m2}  (different objects, but equal values)\n")

    # Currency mismatch
    euros = Money.of(8.50, "EUR")
    try:
        _ = price + euros
    except ValueError as e:
        print(f"Currency mismatch: {e}")

    print("""
NamedTuple as value object:
  - Equality is by value, not identity (auto-generated __eq__)
  - Hashable → usable as dict/set key
  - Immutable → safe to share without copying
  - Lightweight → no __dict__ overhead (tuple-backed)
""")


# =============================================================================
# EXERCISE 4: Dataclass Serialization — asdict() round-trip
# =============================================================================
#
# Build a nested dataclass hierarchy and round-trip through JSON.


class Priority(Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


@dataclass
class Tag:
    name: str
    color: str = "#999999"


@dataclass
class Task:
    title: str
    priority: Priority
    due: date | None
    tags: list[Tag] = field(default_factory=list)
    done: bool = False

    def to_json(self) -> str:
        """Serialize to JSON, handling Enum and date types."""
        def serializer(obj: object) -> object:
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, date):
                return obj.isoformat()
            raise TypeError(f"Not JSON serializable: {type(obj)}")
        return json.dumps(asdict(self), default=serializer, indent=2)

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        """Reconstruct from dict (post-JSON round-trip)."""
        return cls(
            title    = d["title"],
            priority = Priority(d["priority"]),
            due      = date.fromisoformat(d["due"]) if d.get("due") else None,
            tags     = [Tag(**t) for t in d.get("tags", [])],
            done     = d.get("done", False),
        )


def exercise_4_serialization() -> None:
    print("\n=== Exercise 4: Nested Dataclass JSON Serialization ===\n")

    task = Task(
        title    = "Write chapter 5 exercises",
        priority = Priority.HIGH,
        due      = date(2024, 12, 31),
        tags     = [Tag("python"), Tag("dataclass", "#4CAF50")],
    )

    print(f"Task: {task}\n")
    json_str = task.to_json()
    print(f"JSON:\n{json_str}\n")

    # Round-trip
    restored = Task.from_dict(json.loads(json_str))
    print(f"Restored: {restored}")
    print(f"Equal: {task == restored}")
    print(f"Priority type: {type(restored.priority).__name__}")
    print(f"Due type: {type(restored.due).__name__}")


# =============================================================================
# EXERCISE 5: namedtuple._asdict() for CSV/DB export
# =============================================================================
#
# Real-world namedtuple use: typed rows from a database result set.


class CityRecord(NamedTuple):
    """Typed row from a hypothetical cities database query."""
    name: str
    country: str
    population: float        # millions
    latitude: float
    longitude: float
    timezone: str = "UTC"

    def hemisphere(self) -> str:
        ns = "North" if self.latitude >= 0 else "South"
        ew = "East" if self.longitude >= 0 else "West"
        return f"{ns}/{ew}"

    def population_tier(self) -> str:
        if self.population > 20:   return "megacity"
        if self.population > 5:    return "major"
        return "medium"


def exercise_5_namedtuple_database_rows() -> None:
    print("\n=== Exercise 5: NamedTuple as Typed Database Rows ===\n")

    # Simulate DB result rows (could come from cursor.fetchall())
    raw_rows = [
        ("Tokyo",     "JP", 37.4, 35.6895, 139.6917, "Asia/Tokyo"),
        ("Delhi",     "IN", 32.9, 28.6139, 77.2090,  "Asia/Kolkata"),
        ("São Paulo", "BR", 22.0, -23.5505, -46.6333, "America/Sao_Paulo"),
        ("Shanghai",  "CN", 24.9, 31.2304, 121.4737,  "Asia/Shanghai"),
        ("London",    "GB", 9.0,  51.5074, -0.1278,   "Europe/London"),
    ]

    cities = [CityRecord(*row) for row in raw_rows]

    # Sort by population (tuple comparison — no key needed if ordering matches)
    cities.sort(key=lambda c: c.population, reverse=True)

    print(f"  {'Name':<12} {'Country':>8} {'Pop(M)':>8} {'Hemisphere':>15} {'Tier':>10}")
    print("  " + "-" * 58)
    for c in cities:
        print(f"  {c.name:<12} {c.country:>8} {c.population:>8.1f} "
              f"{c.hemisphere():>15} {c.population_tier():>10}")

    # Export to list of dicts (for JSON/pandas)
    as_dicts = [c._asdict() for c in cities]
    print(f"\n._asdict() for JSON: {json.dumps(as_dicts[0], ensure_ascii=False)}")

    # Filter with set operations on namedtuple fields
    megacities = {c.name for c in cities if c.population_tier() == "megacity"}
    print(f"\nMegacities (>20M): {megacities}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    exercise_1_builder_comparison()
    exercise_2_validated_dataclass()
    exercise_3_money_value_object()
    exercise_4_serialization()
    exercise_5_namedtuple_database_rows()
