"""Simple moving-average baseline over the last N minutes of state."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from apps.traffic_state.models import TrafficState

from .base import BasePredictor, PredictionOutput


@dataclass
class MovingAveragePredictor(BasePredictor):
    window_minutes: int = 15
    name: str = "moving_average"
    version: str = "1"

    def predict(
        self, segment_id: int, at: datetime, horizon_minutes: int
    ) -> PredictionOutput:
        start = at - timedelta(minutes=self.window_minutes)
        qs = TrafficState.objects.filter(
            road_id=segment_id, window_start__gte=start, window_start__lte=at
        )
        if not qs.exists():
            return PredictionOutput(None, None, None, 0.0)

        speeds = [s.avg_speed_kmh for s in qs if s.avg_speed_kmh is not None]
        tts = [s.travel_time_s for s in qs if s.travel_time_s is not None]
        ratios = [s.congestion_ratio for s in qs if s.congestion_ratio is not None]

        return PredictionOutput(
            predicted_speed_kmh=sum(speeds) / len(speeds) if speeds else None,
            predicted_travel_time_s=sum(tts) / len(tts) if tts else None,
            predicted_congestion_ratio=sum(ratios) / len(ratios) if ratios else None,
            confidence=min(1.0, qs.count() / 3),
        )
