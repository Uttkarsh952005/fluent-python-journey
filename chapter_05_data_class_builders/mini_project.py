"""
Chapter 5: Mini Project — Schema-Validated Config System
=========================================================
A real-world demonstration of data class builders used together:

  - namedtuple     → immutable, hashable config sections (used as dict keys)
  - NamedTuple     → typed records returned from config parsing
  - @dataclass     → the mutable, validated application config object
  - __post_init__  → validation, computed fields, cross-field constraints
  - ClassVar       → shared registry of registered config keys
  - field()        → default_factory, repr control, metadata

Run with: python mini_project.py
"""

from __future__ import annotations

import json
import os
import sys
from collections import namedtuple
from dataclasses import dataclass, field, fields, asdict
from enum import Enum, auto
from pathlib import Path
from typing import ClassVar, NamedTuple

sys.stdout.reconfigure(encoding="utf-8")


# =============================================================================
# Domain: Application Configuration System
# =============================================================================
# Imagine a web service that loads configuration from a JSON file.
# We want: type safety, validation, defaults, and serialization.


# ─────────────────────────────────────────────────────────────────────────────
# Level 1: namedtuple — immutable config section identifiers (used as keys)
# ─────────────────────────────────────────────────────────────────────────────

ConfigSection = namedtuple("ConfigSection", "service environment")
# Usage: ConfigSection("auth", "production") — hashable, usable as dict key


# ─────────────────────────────────────────────────────────────────────────────
# Level 2: NamedTuple — typed, immutable validation rule descriptor
# ─────────────────────────────────────────────────────────────────────────────

class FieldRule(NamedTuple):
    """Describes a validation rule for one config field."""
    field_name: str
    required: bool
    min_value: float | None = None
    max_value: float | None = None
    allowed_values: tuple[str, ...] | None = None

    def validate(self, value: object) -> list[str]:
        """Returns list of validation error strings (empty = valid)."""
        errors: list[str] = []
        if self.required and value is None:
            errors.append(f"Field '{self.field_name}' is required but missing")
            return errors
        if value is None:
            return errors
        if self.min_value is not None and isinstance(value, (int, float)):
            if value < self.min_value:
                errors.append(f"'{self.field_name}' value {value} < min {self.min_value}")
        if self.max_value is not None and isinstance(value, (int, float)):
            if value > self.max_value:
                errors.append(f"'{self.field_name}' value {value} > max {self.max_value}")
        if self.allowed_values is not None:
            if str(value) not in self.allowed_values:
                errors.append(
                    f"'{self.field_name}' value {value!r} not in {self.allowed_values}"
                )
        return errors


# ─────────────────────────────────────────────────────────────────────────────
# Level 3: Enums for type-safe config values
# ─────────────────────────────────────────────────────────────────────────────

class LogLevel(Enum):
    DEBUG   = "debug"
    INFO    = "info"
    WARNING = "warning"
    ERROR   = "error"


class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING     = "staging"
    PRODUCTION  = "production"


# ─────────────────────────────────────────────────────────────────────────────
# Level 4: @dataclass — the main validated config object
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    host: str
    port: int
    name: str
    user: str
    password: str = field(repr=False)   # excluded from repr for security!
    max_connections: int = 10
    timeout_seconds: float = 30.0

    # Class-level validation rules — shared across all instances
    RULES: ClassVar[list[FieldRule]] = [
        FieldRule("port", required=True, min_value=1, max_value=65535),
        FieldRule("max_connections", required=True, min_value=1, max_value=1000),
        FieldRule("timeout_seconds", required=True, min_value=0.5, max_value=300.0),
    ]

    def __post_init__(self) -> None:
        errors: list[str] = []
        values = asdict(self)
        for rule in self.RULES:
            errors.extend(rule.validate(values.get(rule.field_name)))
        if errors:
            raise ValueError(f"DatabaseConfig validation failed:\n  " + "\n  ".join(errors))

    @property
    def connection_string(self) -> str:
        """Build a safe connection string (no password)."""
        return f"postgresql://{self.user}@{self.host}:{self.port}/{self.name}"


@dataclass
class ServerConfig:
    """HTTP server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 30
    cors_origins: list[str] = field(default_factory=list)

    RULES: ClassVar[list[FieldRule]] = [
        FieldRule("port", required=True, min_value=1, max_value=65535),
        FieldRule("workers", required=True, min_value=1, max_value=64),
    ]

    def __post_init__(self) -> None:
        errors: list[str] = []
        for rule in self.RULES:
            errors.extend(rule.validate(getattr(self, rule.field_name)))
        if errors:
            raise ValueError("ServerConfig validation failed:\n  " + "\n  ".join(errors))


@dataclass
class AppConfig:
    """
    Root application configuration.
    Loads from dict, validates, and provides a clean interface.
    """
    environment: Environment
    log_level: LogLevel
    debug: bool
    database: DatabaseConfig
    server: ServerConfig
    feature_flags: dict[str, bool] = field(default_factory=dict)
    version: str = "1.0.0"
    _section_key: ConfigSection = field(init=False, repr=False, compare=False)

    # Registry of all created configs — class-level tracking
    _registry: ClassVar[dict[ConfigSection, "AppConfig"]] = {}

    def __post_init__(self) -> None:
        # Compute the section key (namedtuple as hashable identifier)
        self._section_key = ConfigSection(
            service="app",
            environment=self.environment.value
        )
        # Register this config
        AppConfig._registry[self._section_key] = self

        # Production-specific validation
        if self.environment == Environment.PRODUCTION:
            if self.debug:
                raise ValueError("debug=True is not allowed in production")
            if self.log_level == LogLevel.DEBUG:
                raise ValueError("LogLevel.DEBUG is not allowed in production")

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        """Factory: construct from raw dictionary (e.g., parsed JSON)."""
        db_data = data["database"]
        srv_data = data.get("server", {})
        return cls(
            environment   = Environment(data["environment"]),
            log_level     = LogLevel(data.get("log_level", "info")),
            debug         = data.get("debug", False),
            database      = DatabaseConfig(**db_data),
            server        = ServerConfig(**srv_data) if srv_data else ServerConfig(),
            feature_flags = data.get("feature_flags", {}),
            version       = data.get("version", "1.0.0"),
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "AppConfig":
        """Load from a JSON file."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    def to_dict(self) -> dict:
        """Serialize to dict (for saving back to JSON)."""
        d = asdict(self)
        # Convert Enum values to their string representation
        d["environment"] = self.environment.value
        d["log_level"]   = self.log_level.value
        return d

    def summary(self) -> str:
        lines = [
            f"  Version:     {self.version}",
            f"  Environment: {self.environment.value}",
            f"  Log level:   {self.log_level.value}",
            f"  Debug:       {self.debug}",
            f"  Database:    {self.database.connection_string}",
            f"  Server:      {self.server.host}:{self.server.port} "
            f"({self.server.workers} workers)",
            f"  Flags:       {self.feature_flags}",
            f"  Section key: {self._section_key}  ← namedtuple used as dict key",
        ]
        return "\n".join(lines)


# =============================================================================
# Config fixtures — simulating different environments
# =============================================================================

DEVELOPMENT_CONFIG: dict = {
    "environment": "development",
    "log_level": "debug",
    "debug": True,
    "version": "2.1.0",
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp_dev",
        "user": "dev_user",
        "password": "dev_password",
        "max_connections": 5,
    },
    "server": {
        "host": "127.0.0.1",
        "port": 8000,
        "workers": 1,
        "cors_origins": ["http://localhost:3000"],
    },
    "feature_flags": {
        "new_dashboard": True,
        "beta_api": True,
    }
}

PRODUCTION_CONFIG: dict = {
    "environment": "production",
    "log_level": "warning",
    "debug": False,
    "version": "2.1.0",
    "database": {
        "host": "db.prod.internal",
        "port": 5432,
        "name": "myapp_prod",
        "user": "prod_user",
        "password": "REDACTED",
        "max_connections": 100,
        "timeout_seconds": 60.0,
    },
    "server": {
        "host": "0.0.0.0",
        "port": 443,
        "workers": 8,
        "cors_origins": ["https://myapp.com"],
    },
    "feature_flags": {
        "new_dashboard": True,
        "beta_api": False,
    }
}


# =============================================================================
# Demo
# =============================================================================

def main() -> None:
    print("=" * 62)
    print("  Schema-Validated Config System")
    print("  Chapter 5 Mini Project — Data Class Builders")
    print("=" * 62)

    # ── Demo 1: Valid development config ─────────────────────────────────────
    print("\n[1] Loading development config\n")
    dev_cfg = AppConfig.from_dict(DEVELOPMENT_CONFIG)
    print(dev_cfg.summary())

    # ── Demo 2: Valid production config ──────────────────────────────────────
    print("\n[2] Loading production config\n")
    prod_cfg = AppConfig.from_dict(PRODUCTION_CONFIG)
    print(prod_cfg.summary())

    # ── Demo 3: Registry lookup using namedtuple as key ──────────────────────
    print("\n[3] Registry lookup — namedtuple as hashable dict key\n")
    key = ConfigSection("app", "development")
    found = AppConfig._registry.get(key)
    print(f"  lookup ConfigSection{key}: found={found is dev_cfg}")
    print(f"  registry size: {len(AppConfig._registry)} entries\n")

    # ── Demo 4: Validation failures ──────────────────────────────────────────
    print("[4] Validation failure cases\n")

    invalid_cases = [
        ("debug=True in production", {**PRODUCTION_CONFIG, "debug": True}),
        ("port out of range", {**DEVELOPMENT_CONFIG, "database": {
            **DEVELOPMENT_CONFIG["database"], "port": 99999
        }}),
        ("max_connections too high", {**DEVELOPMENT_CONFIG, "database": {
            **DEVELOPMENT_CONFIG["database"], "max_connections": 5000
        }}),
    ]

    for desc, bad_config in invalid_cases:
        try:
            AppConfig.from_dict(bad_config)
        except ValueError as e:
            first_line = str(e).split("\n")[0]
            print(f"  [{desc}]: {first_line}")

    # ── Demo 5: FieldRule (NamedTuple) used as validator ─────────────────────
    print("\n[5] FieldRule (NamedTuple) as typed validation descriptor\n")
    rules = [
        FieldRule("age", required=True, min_value=0, max_value=150),
        FieldRule("role", required=True, allowed_values=("admin", "user", "guest")),
        FieldRule("score", required=False, min_value=0.0, max_value=100.0),
    ]

    test_values = [
        ("age", 25),
        ("age", -5),
        ("role", "admin"),
        ("role", "superuser"),
        ("score", None),       # not required — ok
        ("score", 105.0),      # out of range
    ]

    for field_name, value in test_values:
        rule = next(r for r in rules if r.field_name == field_name)
        errors = rule.validate(value)
        status = "✓" if not errors else f"✗ {errors[0]}"
        print(f"  {field_name}={value!r:<12} {status}")

    # ── Demo 6: Serialization round-trip ─────────────────────────────────────
    print("\n[6] Serialization round-trip (asdict → JSON → reconstruct)\n")
    tmp = Path("_ch5_config_test.json")
    d = prod_cfg.to_dict()
    tmp.write_text(json.dumps(d, indent=2), encoding="utf-8")
    restored = AppConfig.from_json(tmp)
    print(f"  environment: {restored.environment.value}")
    print(f"  log_level:   {restored.log_level.value}")
    print(f"  db host:     {restored.database.host}")
    print(f"  Round-trip: environment match = {restored.environment == prod_cfg.environment}")
    tmp.unlink()

    print("\n" + "=" * 62)
    print("  Patterns Demonstrated")
    print("=" * 62)
    print("""
  namedtuple  → ConfigSection: hashable, immutable registry key
  NamedTuple  → FieldRule: typed, immutable validation rule descriptor
  @dataclass  → DatabaseConfig / ServerConfig / AppConfig:
                 mutable, validated, serializable config objects
  ClassVar    → shared rule registry across all instances
  field(repr=False)    → hide password from repr output
  field(compare=False) → exclude fields from equality comparison
  __post_init__        → validation, env-specific constraints
  asdict()             → deep dict for JSON serialization
""")


if __name__ == "__main__":
    main()
