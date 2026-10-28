"""API views.

Wires the routing/network subsystems to REST endpoints. Only the routes
we actively use are implemented; the rest are honest placeholders that
return `not implemented` so the frontend can display disabled states
instead of silently failing.
"""
from __future__ import annotations

import json

import httpx
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.gis.geos import LineString, Point
from django.utils.dateparse import parse_datetime
from django_prometheus.exports import ExportToDjangoView
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from apps.network.models import Corridor, RoadSegment
from apps.prediction.models import ModelVersion
from apps.routing.models import RouteRecommendation, RouteRequest, Strategy
from apps.routing.osrm_client import OSRMClient
from apps.routing.strategies import ConventionalRouting


@api_view(["GET"])
def health(request: Request) -> Response:
    return Response({"status": "ok"})


class RoadSegmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RoadSegment.objects.all()
    serializer_class = None

    def list(self, request, *args, **kwargs):
        limit = min(int(request.query_params.get("limit", 200)), 5000)
        qs = self.get_queryset().values(
            "id", "name", "road_type", "length_m", "speed_limit_kmh"
        )[:limit]
        return Response(list(qs))


class CorridorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Corridor.objects.all()
    serializer_class = None

    def list(self, request, *args, **kwargs):
        return Response(
            [{"id": c.pk, "name": c.name} for c in self.get_queryset()]
        )


class IncidentViewSet(viewsets.ViewSet):
    def list(self, request):
        # TrafficIncident model to be added in a follow-up.
        return Response([])


class ModelVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModelVersion.objects.all()
    serializer_class = None

    def list(self, request, *args, **kwargs):
        return Response(
            [
                {
                    "id": m.pk,
                    "name": m.name,
                    "version": m.version,
                    "algorithm": m.algorithm,
                    "metrics": m.metrics,
                }
                for m in self.get_queryset()
            ]
        )


@api_view(["GET"])
def network_geojson(request: Request) -> Response:
    """FeatureCollection of loaded road segments for the map overlay."""
    limit = min(int(request.query_params.get("limit", 5000)), 20000)
    rows = (
        RoadSegment.objects.annotate(gj=AsGeoJSON("geometry"))
        .values("id", "name", "road_type", "gj")[:limit]
    )
    features = [
        {
            "type": "Feature",
            "id": row["id"],
            "geometry": json.loads(row["gj"]),
            "properties": {"name": row["name"], "road_type": row["road_type"]},
        }
        for row in rows
    ]
    return Response({"type": "FeatureCollection", "features": features})


@api_view(["GET"])
def current_traffic(request: Request) -> Response:
    return Response({"detail": "not implemented", "features": []})


@api_view(["GET"])
def traffic_history(request: Request) -> Response:
    return Response({"detail": "not implemented", "results": []})


@api_view(["GET"])
def traffic_predictions(request: Request) -> Response:
    return Response({"detail": "not implemented", "results": []})


@api_view(["POST"])
def recommend_route(request: Request) -> Response:
    """POST body:

    ```
    {
      "origin": [lon, lat],
      "destination": [lon, lat],
      "departure_time": "2026-08-22T07:30:00+03:00",
      "strategy": "conventional"
    }
    ```
    """
    payload = request.data
    required = {"origin", "destination", "departure_time"}
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

    departure = parse_datetime(payload["departure_time"])
    if departure is None:
        return Response(
            {"error": "invalid departure_time (expected ISO 8601)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    strategy_name = payload.get("strategy", Strategy.CONVENTIONAL)
    if strategy_name != Strategy.CONVENTIONAL:
        return Response(
            {
                "error": (
                    f"strategy '{strategy_name}' requires a trained predictor; "
                    "only 'conventional' is available in this slice."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    client = OSRMClient()
    try:
        candidates = client.route(
            (origin_lon, origin_lat),
            (dest_lon, dest_lat),
            alternatives=3,
        )
    except httpx.HTTPError as exc:
        return Response(
            {"error": "routing engine unavailable", "detail": str(exc)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if not candidates:
        return Response(
            {"error": "no route found"}, status=status.HTTP_404_NOT_FOUND
        )

    scored = ConventionalRouting().rank(candidates, departure)

    route_request = RouteRequest.objects.create(
        origin=Point(origin_lon, origin_lat, srid=4326),
        destination=Point(dest_lon, dest_lat, srid=4326),
        departure_time=departure,
        strategy=strategy_name,
        client_id=str(payload.get("client_id", ""))[:64],
    )

    recommendations_out = []
    for rank, s in enumerate(scored):
        coords = s.route.geometry.get("coordinates", [])
        if len(coords) < 2:
            continue
        RouteRecommendation.objects.create(
            request=route_request,
            rank=rank,
            geometry=LineString(coords, srid=4326),
            current_travel_time_s=s.current_travel_time_s,
            predicted_travel_time_s=s.predicted_travel_time_s,
            risk_level=s.risk_level,
            strategy=s.strategy,
            metadata={"distance_m": s.route.distance_m},
        )
        recommendations_out.append(
            {
                "rank": rank,
                "geometry": s.route.geometry,
                "current_travel_time_s": s.current_travel_time_s,
                "predicted_travel_time_s": s.predicted_travel_time_s,
                "risk_level": s.risk_level,
                "strategy": s.strategy,
                "distance_m": s.route.distance_m,
            }
        )

    return Response(
        {
            "request_id": route_request.pk,
            "strategy": strategy_name,
            "candidates": recommendations_out,
        }
    )


@api_view(["GET"])
def list_routes(request: Request) -> Response:
    limit = min(int(request.query_params.get("limit", 50)), 500)
    qs = RouteRequest.objects.order_by("-requested_at")[:limit]
    return Response(
        [
            {
                "id": r.pk,
                "strategy": r.strategy,
                "departure_time": r.departure_time.isoformat(),
                "requested_at": r.requested_at.isoformat(),
                "candidate_count": r.recommendations.count(),
            }
            for r in qs
        ]
    )


@api_view(["GET"])
def list_simulations(request: Request) -> Response:
    return Response([])


@api_view(["POST"])
def run_simulation(request: Request) -> Response:
    return Response({"detail": "not implemented"}, status=status.HTTP_202_ACCEPTED)


metrics = ExportToDjangoView


def _coerce_lonlat(value) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError("origin/destination must be [lon, lat]")
    lon, lat = float(value[0]), float(value[1])
    if not (-180.0 <= lon <= 180.0) or not (-90.0 <= lat <= 90.0):
        raise ValueError("lon/lat out of range")
    return lon, lat
