"""Routing strategies (brief §23).

Three strategies share a common interface so experiments can hold
network, demand, and seed fixed while swapping strategies:

- ConventionalRouting:  minimises current travel time from OSRM.
- PredictiveRouting:    minimises travel time using per-segment predictions
                        evaluated at the vehicle's *arrival* time (§20).
- NetworkAwareRouting:  additionally accounts for how many vehicles will
                        be simultaneously assigned to each alternative
                        (§21). Placeholder implementation for now — the
                        real assignment loop lives in the optimization
                        engine and needs a running SUMO simulation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Sequence

from .models import Strategy
from .osrm_client import OSRMClient, OSRMRoute


@dataclass
class ScoredRoute:
    route: OSRMRoute
    current_travel_time_s: float
    predicted_travel_time_s: float
    risk_level: str
    strategy: str


class RoutingStrategy(ABC):
    strategy: str = Strategy.CONVENTIONAL

    @abstractmethod
    def rank(
        self,
        candidates: Sequence[OSRMRoute],
        departure_time: datetime,
    ) -> list[ScoredRoute]:
        ...


class ConventionalRouting(RoutingStrategy):
    strategy = Strategy.CONVENTIONAL

    def rank(
        self,
        candidates: Sequence[OSRMRoute],
        departure_time: datetime,
    ) -> list[ScoredRoute]:
        return [
            ScoredRoute(
                route=r,
                current_travel_time_s=r.duration_s,
                predicted_travel_time_s=r.duration_s,
                risk_level="unknown",
                strategy=self.strategy,
            )
            for r in sorted(candidates, key=lambda r: r.duration_s)
        ]


class PredictiveRouting(RoutingStrategy):
    """Score each candidate using predicted state at the arrival time of
    every segment along the route (brief §20)."""

    strategy = Strategy.PREDICTIVE

    def __init__(self, arrival_predictor) -> None:
        # `arrival_predictor` is any callable:
        #     (segment_id, arrival_time) -> predicted_travel_time_s
        self._predict = arrival_predictor

    def rank(
        self,
        candidates: Sequence[OSRMRoute],
        departure_time: datetime,
    ) -> list[ScoredRoute]:
        scored: list[ScoredRoute] = []
        for r in candidates:
            predicted = self._score_route(r, departure_time)
            ratio = predicted / max(r.duration_s, 1.0)
            risk = "low" if ratio < 1.1 else "medium" if ratio < 1.4 else "high"
            scored.append(
                ScoredRoute(
                    route=r,
                    current_travel_time_s=r.duration_s,
                    predicted_travel_time_s=predicted,
                    risk_level=risk,
                    strategy=self.strategy,
                )
            )
        scored.sort(key=lambda s: s.predicted_travel_time_s)
        return scored

    def _score_route(self, route: OSRMRoute, departure: datetime) -> float:
        cumulative_s = 0.0
        total = 0.0
        for leg in route.legs:
            for ann in leg.get("annotation", {}).get("nodes", []) or []:
                pass  # OSRM node IDs; map to internal segment_ids elsewhere.
            duration = float(leg.get("duration", 0.0))
            arrival = departure + timedelta(seconds=cumulative_s)
            # Placeholder: without per-leg segment IDs we fall back to OSRM
            # duration. The real integration lives once network->OSRM node
            # mapping exists.
            predicted_leg = self._predict(None, arrival) or duration
            total += predicted_leg
            cumulative_s += predicted_leg
        return total or route.duration_s


class NetworkAwareRouting(PredictiveRouting):
    """Placeholder — real network-aware assignment lives in the
    optimization engine, which iterates: assign → simulate → re-predict.
    This class exists so the API and experiments can already reference
    the strategy name."""

    strategy = Strategy.NETWORK_AWARE


def build(strategy: str, *, arrival_predictor=None) -> RoutingStrategy:
    """Factory used by the API to instantiate a strategy by name."""
    if strategy == Strategy.CONVENTIONAL:
        return ConventionalRouting()
    if strategy == Strategy.PREDICTIVE:
        if arrival_predictor is None:
            raise ValueError("PredictiveRouting needs an arrival_predictor")
        return PredictiveRouting(arrival_predictor)
    if strategy == Strategy.NETWORK_AWARE:
        if arrival_predictor is None:
            raise ValueError("NetworkAwareRouting needs an arrival_predictor")
        return NetworkAwareRouting(arrival_predictor)
    raise ValueError(f"Unknown strategy: {strategy}")


def default_osrm_client() -> OSRMClient:
    return OSRMClient()
