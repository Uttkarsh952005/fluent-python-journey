"""
Chapter 2: Mini Project — CSV Data Pipeline
============================================
A data processing pipeline demonstrating optimal sequence type selection.

Given a large CSV of sensor readings, this pipeline:
1. Reads data lazily (generator — no full file in memory)
2. Validates rows (generator pipeline — memory efficient)
3. Stores numeric data in array.array (4x less memory than list)
4. Uses memoryview for zero-copy binary export
5. Uses deque for a sliding window anomaly detector
6. Uses named tuples for structured records

This project shows how sequence type selection is an architecture decision,
not just a Python trivia question.

Run with: python mini_project.py
"""

from __future__ import annotations

import array
import csv
import io
import statistics
import sys
from collections import deque, namedtuple
from typing import Generator, Iterator

# Windows PowerShell UTF-8 compatibility
sys.stdout.reconfigure(encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────────────

SensorReading = namedtuple("SensorReading", ["timestamp", "sensor_id", "temperature", "humidity"])


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Stage 1: Lazy CSV Reader (Generator)
# ─────────────────────────────────────────────────────────────────────────────

def generate_sample_csv(n: int = 10_000) -> str:
    """Generate a synthetic CSV dataset in memory (simulates a real file)."""
    import random
    import datetime

    output = io.StringIO()
    output.write("timestamp,sensor_id,temperature,humidity\n")

    base_time = datetime.datetime(2026, 1, 1, 0, 0, 0)
    for i in range(n):
        ts = base_time + datetime.timedelta(minutes=i)
        sensor_id = f"S{(i % 5) + 1:02d}"
        temp = round(20 + random.gauss(0, 5), 2)
        humidity = round(50 + random.gauss(0, 10), 2)
        output.write(f"{ts.isoformat()},{sensor_id},{temp},{humidity}\n")

    return output.getvalue()


def read_csv_lazy(csv_text: str) -> Generator[SensorReading, None, None]:
    """
    STAGE 1: Read CSV lazily as a generator.
    Yields one SensorReading at a time — never loads the full file into memory.

    This is the difference between:
        all_rows = list(csv.reader(f))       # 100 MB file in RAM
        rows = csv_reader_generator(f)        # Constant memory
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        try:
            yield SensorReading(
                timestamp=row["timestamp"],
                sensor_id=row["sensor_id"],
                temperature=float(row["temperature"]),
                humidity=float(row["humidity"]),
            )
        except (ValueError, KeyError):
            continue  # Skip malformed rows


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Stage 2: Validation Filter (Generator)
# ─────────────────────────────────────────────────────────────────────────────

def validate_readings(
    readings: Iterator[SensorReading],
    temp_range: tuple[float, float] = (-40.0, 85.0),
    humidity_range: tuple[float, float] = (0.0, 100.0),
) -> Generator[SensorReading, None, None]:
    """
    STAGE 2: Filter invalid readings as a generator.
    Composable with any iterator upstream — no coupling to CSV specifics.
    """
    low_t, high_t = temp_range
    low_h, high_h = humidity_range
    for reading in readings:
        if low_t <= reading.temperature <= high_t and low_h <= reading.humidity <= high_h:
            yield reading


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Stage 3: Compact Storage (array.array)
# ─────────────────────────────────────────────────────────────────────────────

class SensorStore:
    """
    STAGE 3: Memory-efficient storage using array.array.
    Stores temperature and humidity as C doubles — 4x less memory than list of floats.
    """

    def __init__(self) -> None:
        self.temperatures: array.array[float] = array.array("d")  # C doubles
        self.humidities: array.array[float] = array.array("d")
        self.sensor_ids: list[str] = []

    def ingest(self, readings: Iterator[SensorReading]) -> int:
        """Consume the pipeline and store data efficiently."""
        count = 0
        for reading in readings:
            self.temperatures.append(reading.temperature)
            self.humidities.append(reading.humidity)
            self.sensor_ids.append(reading.sensor_id)
            count += 1
        return count

    def memory_report(self) -> dict[str, int]:
        temp_mem = sys.getsizeof(self.temperatures)
        humid_mem = sys.getsizeof(self.humidities)
        ids_mem = sys.getsizeof(self.sensor_ids) + sum(
            sys.getsizeof(s) for s in self.sensor_ids
        )
        return {
            "temperatures_bytes": temp_mem,
            "humidities_bytes": humid_mem,
            "sensor_ids_bytes": ids_mem,
            "total_bytes": temp_mem + humid_mem + ids_mem,
        }

    def statistics_report(self) -> dict[str, float]:
        temps = self.temperatures
        return {
            "count": len(temps),
            "mean_temp": statistics.mean(temps),
            "stdev_temp": statistics.stdev(temps),
            "min_temp": min(temps),
            "max_temp": max(temps),
        }

    def export_binary(self) -> memoryview:
        """
        Export temperatures as a raw binary buffer (memoryview).
        The receiver can slice this view without copying any data.
        """
        return memoryview(self.temperatures)


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Stage 4: Anomaly Detection (deque sliding window)
# ─────────────────────────────────────────────────────────────────────────────

class AnomalyDetector:
    """
    STAGE 4: Detect temperature anomalies using a sliding window.
    Uses deque(maxlen=N) as an efficient ring buffer — O(1) push and auto-eviction.
    """

    def __init__(self, window_size: int = 20, z_threshold: float = 2.5) -> None:
        self.window: deque[float] = deque(maxlen=window_size)
        self.z_threshold = z_threshold
        self.anomalies: list[tuple[int, float, float]] = []  # (index, value, z_score)

    def process(self, temperatures: array.array[float]) -> None:
        """Scan temperatures for anomalies using a sliding window z-score."""
        for i, temp in enumerate(temperatures):
            if len(self.window) >= 3:
                mean = statistics.mean(self.window)
                stdev = statistics.stdev(self.window)
                if stdev > 0:
                    z = abs((temp - mean) / stdev)
                    if z > self.z_threshold:
                        self.anomalies.append((i, temp, round(z, 2)))
            self.window.append(temp)

    def report(self) -> None:
        if not self.anomalies:
            print("  [OK] No anomalies detected")
        else:
            print(f"  [WARN] {len(self.anomalies)} anomalies found:")
            for idx, val, z in self.anomalies[:5]:  # Show first 5
                print(f"     Index {idx:5d}: temp={val:7.2f}C  z-score={z:.2f}")
            if len(self.anomalies) > 5:
                print(f"     ... and {len(self.anomalies) - 5} more")


# ─────────────────────────────────────────────────────────────────────────────
# Main: Compose the pipeline
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Sensor Data Pipeline -- Sequence Types Demo")
    print("=" * 60)

    # -- Generate synthetic data --
    N = 10_000
    print(f"\n[GEN] Generating {N:,} sensor readings...")
    csv_data = generate_sample_csv(N)
    print(f"   CSV size: {sys.getsizeof(csv_data) / 1024:.0f} KB")

    # Compose the generator pipeline (these are lazy -- no data yet):
    raw_readings = read_csv_lazy(csv_data)
    valid_readings = validate_readings(raw_readings, temp_range=(-10.0, 50.0))

    # -- Ingest into compact storage --
    print("\n[INGEST] Ingesting into SensorStore...")
    store = SensorStore()
    count = store.ingest(valid_readings)

    mem = store.memory_report()
    print(f"   Ingested: {count:,} readings")
    print(f"   Memory used: {mem['total_bytes'] / 1024:.1f} KB")

    # Compare with naive list storage:
    naive_list_size = count * (2 * 28)  # 2 Python floats per reading, 28 bytes each
    print(f"   Naive list equivalent: ~{naive_list_size / 1024:.1f} KB")
    print(f"   array.array savings: {naive_list_size / mem['total_bytes']:.1f}x less memory for numerics")

    # -- Statistics --
    stats = store.statistics_report()
    print(f"\n[STATS] Temperature Statistics:")
    print(f"   Count: {stats['count']:,}")
    print(f"   Mean:  {stats['mean_temp']:+.2f}°C")
    print(f"   Stdev: {stats['stdev_temp']:.2f}°C")
    print(f"   Range: {stats['min_temp']:.2f}°C to {stats['max_temp']:.2f}°C")

    # -- Anomaly detection --
    print(f"\n[SCAN] Running anomaly detection (window=20, z>{2.5})...")
    detector = AnomalyDetector(window_size=20, z_threshold=2.5)
    detector.process(store.temperatures)
    detector.report()

    # -- Zero-copy binary export --
    print(f"\n[EXPORT] Exporting temperature data as binary...")
    binary_view = store.export_binary()
    print(f"   memoryview: {binary_view.nbytes:,} bytes, format='{binary_view.format}'")
    print(f"   Slicing binary_view[0:100] copies 0 bytes — zero-copy!")
    chunk = binary_view[0:100]  # No allocation
    print(f"   First 5 temps: {list(chunk.tolist()[:5])}")

    print("\n[DONE] Pipeline complete -- sequence type selection was deliberate:")
    print("   Generator pipeline -> O(1) memory for CSV reading")
    print("   array.array        -> 4x memory savings for numeric data")
    print("   deque(maxlen)      -> O(1) sliding window with auto-eviction")
    print("   memoryview         -> Zero-copy binary export")


if __name__ == "__main__":
    main()
