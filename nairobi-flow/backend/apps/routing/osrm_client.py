"""Thin OSRM HTTP client.

Only wraps the route + alternatives endpoint. The traffic intelligence
layer (see strategies.py) is intentionally separate — OSRM stays a
candidate-route generator, not a traffic predictor.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from django.conf import settings


@dataclass
class OSRMRoute:
    geometry: dict[str, Any]
    duration_s: float
    distance_m: float
    legs: list[dict[str, Any]]


class OSRMClient:
    def __init__(self, base_url: str | None = None, timeout_s: float = 5.0) -> None:
        self.base_url = (base_url or settings.OSRM_BASE_URL).rstrip("/")
        self.timeout_s = timeout_s

    def route(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        alternatives: int = 3,
        profile: str = "driving",
    ) -> list[OSRMRoute]:
        """Return up to `alternatives + 1` candidate routes."""
        coords = f"{origin[0]},{origin[1]};{destination[0]},{destination[1]}"
        url = f"{self.base_url}/route/v1/{profile}/{coords}"
        params = {
            "alternatives": str(alternatives),
            "geometries": "geojson",
            "overview": "full",
            "steps": "false",
            "annotations": "duration,distance,nodes",
        }
        with httpx.Client(timeout=self.timeout_s) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        return [
            OSRMRoute(
                geometry=r["geometry"],
                duration_s=float(r["duration"]),
                distance_m=float(r["distance"]),
                legs=r.get("legs", []),
            )
            for r in data.get("routes", [])
        ]
