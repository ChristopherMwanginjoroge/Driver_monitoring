"""Generic TrafficDataSource interface.

Any new traffic input (SUMO, GPS, camera, public dataset, government
feed, external benchmark, …) plugs in by subclassing `TrafficDataSource`
and yielding standard `TrafficObservationRecord` objects.

Nothing downstream depends on a specific provider.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable


@dataclass(frozen=True)
class TrafficObservationRecord:
    """Standardized observation as defined in the project brief §9."""

    timestamp: datetime
    latitude: float | None = None
    longitude: float | None = None
    road_id: int | None = None
    speed_kmh: float | None = None
    vehicle_count: int | None = None
    density_vpk: float | None = None
    travel_time_s: float | None = None
    source: str = "unknown"
    confidence: float = 1.0
    payload: dict[str, Any] = field(default_factory=dict)


class TrafficDataSource(ABC):
    """Base class for pluggable traffic-observation sources."""

    #: Short identifier — must match one of ObservationSource choices.
    source_name: str = "unknown"

    @abstractmethod
    def stream(self) -> Iterable[TrafficObservationRecord]:
        """Yield standardized observations.

        Implementations may pull from a file, TraCI (SUMO), an HTTP feed,
        a video pipeline, etc. They must not persist to the database
        directly — persistence is the ingestion layer's job.
        """
