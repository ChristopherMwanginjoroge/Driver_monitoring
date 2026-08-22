"""Predictor contract.

All predictors — baseline or ML — implement `BasePredictor.predict`.
Selection is measurement-driven: a new model only replaces the current
one when MAE/RMSE improve on held-out data. Never assume DL is superior.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PredictionOutput:
    predicted_speed_kmh: float | None
    predicted_travel_time_s: float | None
    predicted_congestion_ratio: float | None
    confidence: float


class BasePredictor(ABC):
    #: Free-text name recorded on ModelVersion.
    name: str = "base"
    version: str = "0"

    @abstractmethod
    def predict(
        self,
        segment_id: int,
        at: datetime,
        horizon_minutes: int,
    ) -> PredictionOutput:
        """Predict segment state `horizon_minutes` from `at`."""
