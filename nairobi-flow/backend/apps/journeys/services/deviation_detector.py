"""Deviation detection: decide whether the driver has left the planned route."""

from __future__ import annotations

from typing import Any

from django.contrib.gis.geos import LineString, Point


def is_deviating(
    lon: float,
    lat: float,
    route_geometry: LineString | None,
    threshold_m: float = 40.0,
) -> tuple[bool, float | None]:
    """Return (is_deviating, distance_m) for a GPS point vs the route.

    A driver is flagged as deviating when their position is farther than
    ``threshold_m`` from the nearest point on the planned route geometry.
    """
    if route_geometry is None:
        return False, None

    point = Point(lon, lat, srid=4326)
    min_dist: float | None = None

    coords = route_geometry.coords
    for i in range(len(coords) - 1):
        a = coords[i]
        b = coords[i + 1]
        seg = LineString([a, b], srid=4326)
        proj = seg.interpolate(seg.project(point))
        d = point.distance(proj) * 111_320
        if min_dist is None or d < min_dist:
            min_dist = d

    if min_dist is None:
        return False, None

    return min_dist > threshold_m, min_dist


def next_turn_from_steps(
    steps: list[dict[str, Any]],
    distance_traveled_m: float,
) -> dict[str, Any] | None:
    """Pick the next upcoming turn step given distance traveled along route.

    Returns the first step whose cumulative distance exceeds the traveled
    distance, plus its distance remaining.
    """
    cumulative = 0.0
    for step in steps:
        step_dist = float(step.get("distance", 0.0) or 0.0)
        if cumulative + step_dist > distance_traveled_m:
            return {
                "instruction": (
                    (step.get("maneuver") or {}).get("instruction", "Continue")
                ),
                "distance_remaining_m": max(cumulative + step_dist - distance_traveled_m, 0.0),
                "type": (step.get("maneuver") or {}).get("type", ""),
                "modifier": (step.get("maneuver") or {}).get("modifier"),
            }
        cumulative += step_dist
    return None