"""External benchmark source.

Represents legally, manually collected data points from commercial
systems (Google Maps, HERE, Waze, TomTom) used only for validation and
comparison. This source **must never** be required at runtime.
Persisted rows should be tagged so they are excluded from training.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .base import TrafficDataSource, TrafficObservationRecord


@dataclass
class ExternalBenchmarkSource(TrafficDataSource):
    records: list[TrafficObservationRecord]
    provider: str = "unknown"
    source_name: str = "external_benchmark"

    def stream(self) -> Iterable[TrafficObservationRecord]:
        for r in self.records:
            yield TrafficObservationRecord(
                timestamp=r.timestamp,
                latitude=r.latitude,
                longitude=r.longitude,
                road_id=r.road_id,
                speed_kmh=r.speed_kmh,
                vehicle_count=r.vehicle_count,
                density_vpk=r.density_vpk,
                travel_time_s=r.travel_time_s,
                source=self.source_name,
                confidence=r.confidence,
                payload={**r.payload, "provider": self.provider, "benchmark_only": True},
            )
