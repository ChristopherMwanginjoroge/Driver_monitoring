"""Serializers for traffic observations API endpoints."""
from __future__ import annotations

from rest_framework import serializers

from apps.observations.models import TrafficObservation


class TrafficObservationSerializer(serializers.ModelSerializer):
    """Serializer for TrafficObservation model.

    Exposes all observation fields including map-matched segment ID,
    match confidence, and raw GPS coordinates for debugging.
    """

    class Meta:
        model = TrafficObservation
        fields = [
            "id",
            "road",
            "timestamp",
            "location",
            "speed_kmh",
            "vehicle_count",
            "density_vpk",
            "travel_time_s",
            "source",
            "confidence",
            "matched_segment_id",
            "match_confidence",
            "raw_lat_lon",
            "payload",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "matched_segment_id",
            "match_confidence",
            "raw_lat_lon",
            "created_at",
        ]


class TrafficObservationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints."""

    class Meta:
        model = TrafficObservation
        fields = [
            "id",
            "timestamp",
            "source",
            "speed_kmh",
            "matched_segment_id",
            "match_confidence",
        ]
