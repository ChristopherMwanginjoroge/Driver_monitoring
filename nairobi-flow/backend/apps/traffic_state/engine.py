"""Traffic-state estimation engine.

Consumes recent `TrafficObservation` rows and produces per-segment
`TrafficState` rows. Thresholds for congestion are derived from
`congestion_ratio = current_speed / free_flow_speed` — never hard-coded
without justification (see brief §12).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import median

from django.db.models import Avg, Count

from apps.network.models import RoadSegment
from apps.observations.models import TrafficObservation

from .models import CongestionLevel, TrafficState


# Ratio-based congestion classification. Ratios (current/free-flow):
#   > 0.75  → free flow
#   > 0.55  → light
#   > 0.40  → moderate
#   > 0.25  → heavy
#   ≤ 0.25  → severe
# These are working defaults for the MVP; they will be recalibrated as
# real Nairobi data becomes available (see docs/PROJECT_BRIEF.md §12).
_RATIO_THRESHOLDS = (
    (0.75, CongestionLevel.FREE_FLOW),
    (0.55, CongestionLevel.LIGHT),
    (0.40, CongestionLevel.MODERATE),
    (0.25, CongestionLevel.HEAVY),
)


@dataclass
class WindowedEstimator:
    window: timedelta = timedelta(minutes=5)

    def estimate(self, segment: RoadSegment, at: datetime) -> TrafficState | None:
        start = at - self.window
        qs = TrafficObservation.objects.filter(
            road=segment, timestamp__gte=start, timestamp__lt=at
        ).exclude(speed_kmh__isnull=True)

        speeds = list(qs.values_list("speed_kmh", flat=True))
        if not speeds:
            return None

        agg = qs.aggregate(
            avg_speed=Avg("speed_kmh"),
            count=Count("id"),
            avg_travel_time=Avg("travel_time_s"),
            avg_density=Avg("density_vpk"),
        )
        avg_speed = agg["avg_speed"]
        med_speed = median(speeds)
        free_flow = segment.free_flow_speed_kmh or segment.speed_limit_kmh
        ratio = (avg_speed / free_flow) if free_flow else None

        state, _ = TrafficState.objects.update_or_create(
            road=segment,
            window_start=start,
            defaults={
                "window_end": at,
                "avg_speed_kmh": avg_speed,
                "median_speed_kmh": med_speed,
                "vehicle_count": agg["count"],
                "travel_time_s": agg["avg_travel_time"],
                "density_vpk": agg["avg_density"],
                "congestion_ratio": ratio,
                "congestion_level": _classify(ratio),
                "confidence": min(1.0, agg["count"] / 5.0),
                "observation_count": agg["count"],
            },
        )
        return state


def _classify(ratio: float | None) -> str:
    if ratio is None:
        return CongestionLevel.FREE_FLOW
    for threshold, level in _RATIO_THRESHOLDS:
        if ratio > threshold:
            return level
    return CongestionLevel.SEVERE
