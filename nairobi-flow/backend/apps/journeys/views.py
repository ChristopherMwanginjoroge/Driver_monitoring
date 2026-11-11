"""Journey views: start, location update, state, pause/resume/reroute/complete."""

from __future__ import annotations

import uuid

from django.contrib.gis.geos import LineString, Point
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from apps.routing.osrm_client import OSRMClient

from .models import Journey, JourneyLocation
from .serializers import JourneySerializer
from .services.deviation_detector import is_deviating, next_turn_from_steps
from .services.map_matcher import snap_to_route


@api_view(["POST"])
def journey_start(request: Request) -> Response:
    """Create a new navigation journey.

    Body:
    {
      "origin": [lon, lat],
      "destination": [lon, lat],
      "route_geometry": { "type": "LineString", "coordinates": [...] },
      "route_distance_m": 12345,
      "route_duration_s": 1800,
      "client_id": "optional-client-id"
    }
    """
    payload = request.data
    required = {"origin", "destination", "route_geometry"}
    missing = required - payload.keys()
    if missing:
        return Response(
            {"error": f"missing fields: {sorted(missing)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        origin_lon, origin_lat = _coerce_lonlat(payload["origin"])
        dest_lon, dest_lat = _coerce_lonlat(payload["destination"])
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    rg = payload.get("route_geometry")
    if rg.get("type") != "LineString":
        return Response(
            {"error": "route_geometry must be a LineString"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    coords = rg.get("coordinates", [])
    if len(coords) < 2:
        return Response(
            {"error": "route_geometry needs at least 2 coordinates"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    route_geom = LineString(coords, srid=4326)

    # Extract turn-by-turn steps from OSRM for the selected route.
    route_steps: list[dict] = []
    try:
        client = OSRMClient()
        routes = client.route(
            (origin_lon, origin_lat),
            (dest_lon, dest_lat),
            alternatives=0,
        )
        if routes:
            route_steps = [
                {
                    "instruction": s.instruction,
                    "distance_m": s.distance_m,
                    "duration_s": s.duration_s,
                    "type": s.type,
                    "modifier": s.modifier,
                    "location": s.location,
                }
                for s in routes[0].steps
            ]
    except Exception:
        # Non-fatal: continue without turn-by-turn steps.
        route_steps = []

    journey = Journey.objects.create(
        id=str(uuid.uuid4()),
        origin=Point(origin_lon, origin_lat, srid=4326),
        destination=Point(dest_lon, dest_lat, srid=4326),
        selected_route_geometry=route_geom,
        selected_route_distance_m=payload.get("route_distance_m"),
        selected_route_duration_s=payload.get("route_duration_s"),
        route_steps=route_steps,
        status=Journey.Status.ACTIVE,
        client_id=str(payload.get("client_id", ""))[:64],
    )
    JourneyLocation.objects.create(
        journey=journey,
        position=Point(origin_lon, origin_lat, srid=4326),
        timestamp=timezone.now(),
    )

    return Response(JourneySerializer(journey).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def journey_location(request: Request, journey_id: str) -> Response:
    """Submit a GPS update for an active journey.

    Performs map matching, deviation detection, turn-by-turn progression,
    and automatic rerouting when the driver leaves the route.
    """
    journey = get_object_or_404(Journey, id=journey_id)
    if journey.status != Journey.Status.ACTIVE:
        return Response(
            {"error": f"journey is {journey.status}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payload = request.data
    try:
        lon = float(payload["longitude"])
        lat = float(payload["latitude"])
    except (KeyError, ValueError, TypeError) as exc:
        return Response(
            {"error": f"invalid coordinates: {exc}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    speed = payload.get("speed_kmh")
    heading = payload.get("heading_deg")
    accuracy = payload.get("accuracy_m")
    ts_str = payload.get("timestamp")
    ts = timezone.now()
    if ts_str:
        from django.utils.dateparse import parse_datetime

        parsed = parse_datetime(ts_str)
        if parsed:
            ts = parsed

    # Store the raw GPS sample.
    JourneyLocation.objects.create(
        journey=journey,
        position=Point(lon, lat, srid=4326),
        speed_kmh=speed,
        heading_deg=heading,
        accuracy_m=accuracy,
        timestamp=ts,
    )

    # Map-match to the route.
    matched_point, match_dist, seg_idx = snap_to_route(
        lon, lat, journey.selected_route_geometry
    )

    # Deviation detection.
    deviating, dev_dist = is_deviating(
        lon, lat, journey.selected_route_geometry, threshold_m=40.0
    )

    # Compute distance traveled along route (approx: origin -> current position).
    distance_traveled_m = 0.0
    if journey.selected_route_geometry and journey.origin:
        try:
            from django.contrib.gis.measure import Distance

            d = journey.selected_route_geometry.distance(
                Point(lon, lat, srid=4326)
            )
            distance_traveled_m = d * 111_320
        except Exception:
            distance_traveled_m = 0.0

    # Next turn from steps.
    next_turn = next_turn_from_steps(journey.route_steps or [], distance_traveled_m)

    # Update journey state.
    journey.current_position = Point(lon, lat, srid=4326)
    journey.distance_remaining_m = (
        journey.selected_route_distance_m - distance_traveled_m
        if journey.selected_route_distance_m
        else None
    )
    if journey.distance_remaining_m is not None:
        journey.distance_remaining_m = max(journey.distance_remaining_m, 0)
    if next_turn:
        journey.next_turn_instruction = next_turn["instruction"]
        journey.next_turn_distance_m = next_turn["distance_remaining_m"]
    else:
        journey.next_turn_instruction = "Continue on route"
        journey.next_turn_distance_m = None

    # Auto-reroute if deviating beyond threshold.
    rerouted = False
    if deviating:
        try:
            client = OSRMClient()
            new_routes = client.route(
                (lon, lat),
                (journey.destination.x, journey.destination.y),
                alternatives=0,
            )
            if new_routes:
                nr = new_routes[0]
                journey.selected_route_geometry = LineString(
                    nr.geometry["coordinates"], srid=4326
                )
                journey.selected_route_distance_m = nr.distance_m
                journey.selected_route_duration_s = nr.duration_s
                journey.route_steps = [
                    {
                        "instruction": s.instruction,
                        "distance_m": s.distance_m,
                        "duration_s": s.duration_s,
                        "type": s.type,
                        "modifier": s.modifier,
                        "location": s.location,
                    }
                    for s in nr.steps
                ]
                journey.distance_remaining_m = nr.distance_m
                journey.next_turn_instruction = "Rerouted — continue on new route"
                journey.next_turn_distance_m = None
                rerouted = True
        except Exception:
            # OSRM unavailable — keep current route, driver is off-route.
            pass

    journey.save()

    return Response(
        {
            **JourneySerializer(journey).data,
            "map_matched": {
                "matched": match_dist is not None and match_dist <= 40.0,
                "distance_to_route_m": match_dist,
            },
            "deviating": deviating,
            "deviation_distance_m": dev_dist,
            "rerouted": rerouted,
        }
    )


@api_view(["GET"])
def journey_state(request: Request, journey_id: str) -> Response:
    """Retrieve current journey state."""
    journey = get_object_or_404(Journey, id=journey_id)
    return Response(JourneySerializer(journey).data)


@api_view(["POST"])
def journey_pause(request: Request, journey_id: str) -> Response:
    journey = get_object_or_404(Journey, id=journey_id)
    journey.status = Journey.Status.PAUSED
    journey.save(update_fields=["status", "updated_at"])
    return Response(JourneySerializer(journey).data)


@api_view(["POST"])
def journey_resume(request: Request, journey_id: str) -> Response:
    journey = get_object_or_404(Journey, id=journey_id)
    journey.status = Journey.Status.ACTIVE
    journey.save(update_fields=["status", "updated_at"])
    return Response(JourneySerializer(journey).data)


@api_view(["POST"])
def journey_complete(request: Request, journey_id: str) -> Response:
    journey = get_object_or_404(Journey, id=journey_id)
    journey.status = Journey.Status.COMPLETED
    journey.ended_at = timezone.now()
    journey.save(update_fields=["status", "ended_at", "updated_at"])
    return Response(
        {
            "id": journey.id,
            "status": journey.status,
            "ended_at": journey.ended_at.isoformat(),
            "distance_remaining_m": journey.distance_remaining_m,
        }
    )


@api_view(["POST"])
def journey_reroute(request: Request, journey_id: str) -> Response:
    """Trigger a fresh route recommendation from current position."""
    journey = get_object_or_404(Journey, id=journey_id)
    if journey.status not in (Journey.Status.ACTIVE, Journey.Status.PAUSED):
        return Response(
            {"error": f"cannot reroute a {journey.status} journey"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(
        {
            "journey_id": journey.id,
            "detail": "reroute requested — call /api/routes/recommend/ from current position",
        }
    )


def _coerce_lonlat(value) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError("origin/destination must be [lon, lat]")
    lon, lat = float(value[0]), float(value[1])
    if not (-180.0 <= lon <= 180.0) or not (-90.0 <= lat <= 90.0):
        raise ValueError("lon/lat out of range")
    return lon, lat