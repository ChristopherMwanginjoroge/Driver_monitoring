"""Historical-average baseline.

Predicts the segment's mean state at the same (weekday, hour, minute)
bucket over a rolling history window.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.db.models import Avg

from apps.traffic_state.models import TrafficState

from .base import BasePredictor, PredictionOutput


@dataclass
class HistoricalAveragePredictor(BasePredictor):
    lookback_days: int = 30
    minute_bucket: int = 5
    name: str = "historical_average"
    version: str = "1"

    def predict(
        self, segment_id: int, at: datetime, horizon_minutes: int
    ) -> PredictionOutput:
        target = at + timedelta(minutes=horizon_minutes)
        target_bucket = (target.hour * 60 + target.minute) // self.minute_bucket
        start = at - timedelta(days=self.lookback_days)

        qs = TrafficState.objects.filter(
            road_id=segment_id,
            window_start__gte=start,
            window_start__week_day=target.isoweekday() % 7 + 1,
        )
        matches = [
            s
            for s in qs
            if (s.window_start.hour * 60 + s.window_start.minute) // self.minute_bucket
            == target_bucket
        ]
        if not matches:
            return PredictionOutput(None, None, None, 0.0)

        avg_speed = _mean(s.avg_speed_kmh for s in matches)
        avg_tt = _mean(s.travel_time_s for s in matches)
        avg_ratio = _mean(s.congestion_ratio for s in matches)
        return PredictionOutput(avg_speed, avg_tt, avg_ratio, min(1.0, len(matches) / 5))


def _mean(values) -> float | None:
    values = [v for v in values if v is not None]
    if not values:
        return None
    return sum(values) / len(values)
