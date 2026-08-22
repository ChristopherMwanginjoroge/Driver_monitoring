"""Manual traffic count source.

Reads a CSV of manually collected counts. Useful early in the project
before GPS/CV pipelines exist.

Expected columns (case-insensitive):
    timestamp, road_id, vehicle_count, [speed_kmh, travel_time_s, notes]
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .base import TrafficDataSource, TrafficObservationRecord


@dataclass
class ManualCountSource(TrafficDataSource):
    csv_path: Path
    source_name: str = "manual"

    def stream(self) -> Iterable[TrafficObservationRecord]:
        with self.csv_path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                yield TrafficObservationRecord(
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    road_id=int(row["road_id"]) if row.get("road_id") else None,
                    vehicle_count=int(row["vehicle_count"])
                    if row.get("vehicle_count")
                    else None,
                    speed_kmh=float(row["speed_kmh"]) if row.get("speed_kmh") else None,
                    travel_time_s=float(row["travel_time_s"])
                    if row.get("travel_time_s")
                    else None,
                    source=self.source_name,
                    payload={"notes": row.get("notes", "")},
                )
