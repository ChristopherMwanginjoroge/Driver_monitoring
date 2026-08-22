"""GPS probe source.

Ingests anonymized GPS observations submitted by consenting clients.
Points are validated (basic sanity) and passed on for map-matching by
the ingestion layer — this source itself does not map-match.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .base import TrafficDataSource, TrafficObservationRecord


@dataclass
class GPSSource(TrafficDataSource):
    records: list[TrafficObservationRecord]
    source_name: str = "gps"

    def stream(self) -> Iterable[TrafficObservationRecord]:
        for r in self.records:
            if not self._valid(r):
                continue
            yield r

    @staticmethod
    def _valid(r: TrafficObservationRecord) -> bool:
        if r.latitude is None or r.longitude is None:
            return False
        if not (-90.0 <= r.latitude <= 90.0):
            return False
        if not (-180.0 <= r.longitude <= 180.0):
            return False
        if r.speed_kmh is not None and (r.speed_kmh < 0 or r.speed_kmh > 250):
            return False
        return True
