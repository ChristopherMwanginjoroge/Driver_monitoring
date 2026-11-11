"""Map matching: snap GPS positions to the nearest route segment."""

from __future__ import annotations

from typing import Any

from django.contrib.gis.geos import LineString, Point


def snap_to_route(
    lon: float,
    lat: float,
    route_geometry: LineString | None,
    search_radius_m: float = 50.0,
) -> tuple[Point | None, float | None, int | None]:
    """Snap a GPS point to the nearest point on the route LineString.

    Returns (matched_point, distance_m, nearest_segment_index) or
    (None, None, None) if no route geometry is available.

    This is a lightweight projection-based matcher: it finds the closest
    vertex on the route geometry and projects the GPS point onto the
    incident segment. For production, replace with a proper
    OSRM/map-matching integration.
    """
    if route_geometry is None:
        return None, None, None

    point = Point(lon, lat, srid=4326)
    coords = route_geometry.coords

    best_point: Point | None = None
    best_dist: float | None = None
    best_seg: int | None = None

    for i in range(len(coords) - 1):
        a = coords[i]
        b = coords[i + 1]
        seg = LineString([a, b], srid=4326)
        # Project point onto segment; fall back to nearest vertex.
        proj = seg.interpolate(seg.project(point))
        d = point.distance(proj) * 111_320  # rough deg -> metres
        if best_dist is None or d < best_dist:
            best_dist = d
            best_point = proj
            best_seg = i

    if best_dist is not None and best_dist > search_radius_m:
        # Point is too far from the route — likely a deviation.
        return best_point, best_dist, best_seg

    return best_point, best_dist, best_seg