from .base import BasePredictor, PredictionOutput
from .historical_average import HistoricalAveragePredictor
from .moving_average import MovingAveragePredictor

__all__ = [
    "BasePredictor",
    "PredictionOutput",
    "HistoricalAveragePredictor",
    "MovingAveragePredictor",
]
