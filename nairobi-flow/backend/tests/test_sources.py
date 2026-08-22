"""Smoke tests that exercise pure-Python paths without a database."""
from datetime import datetime, timezone

from apps.observations.sources.base import TrafficObservationRecord
from apps.observations.sources.gps import GPSSource
from apps.observations.sources.external_benchmark import ExternalBenchmarkSource


def test_gps_source_filters_invalid_points() -> None:
    now = datetime.now(timezone.utc)
    valid = TrafficObservationRecord(
        timestamp=now, latitude=-1.28, longitude=36.82, speed_kmh=30.0
    )
    bad_lat = TrafficObservationRecord(
        timestamp=now, latitude=999.0, longitude=36.82, speed_kmh=30.0
    )
    bad_speed = TrafficObservationRecord(
        timestamp=now, latitude=-1.28, longitude=36.82, speed_kmh=-5.0
    )
    src = GPSSource(records=[valid, bad_lat, bad_speed])
    out = list(src.stream())
    assert len(out) == 1
    assert out[0].latitude == -1.28


def test_external_benchmark_marks_records() -> None:
    now = datetime.now(timezone.utc)
    r = TrafficObservationRecord(
        timestamp=now, latitude=-1.28, longitude=36.82, speed_kmh=25.0
    )
    src = ExternalBenchmarkSource(records=[r], provider="google_maps")
    tagged = list(src.stream())
    assert tagged[0].source == "external_benchmark"
    assert tagged[0].payload["provider"] == "google_maps"
    assert tagged[0].payload["benchmark_only"] is True
