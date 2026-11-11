"""Journey serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import Journey, JourneyLocation


class JourneyLocationSerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    class Meta:
        model = JourneyLocation
        fields = [
            "longitude",
            "latitude",
            "speed_kmh",
            "heading_deg",
            "accuracy_m",
            "timestamp",
        ]

    def get_longitude(self, obj):
        return obj.position.x if obj.position else None

    def get_latitude(self, obj):
        return obj.position.y if obj.position else None


class JourneySerializer(serializers.ModelSerializer):
    origin_lon = serializers.SerializerMethodField()
    origin_lat = serializers.SerializerMethodField()
    destination_lon = serializers.SerializerMethodField()
    destination_lat = serializers.SerializerMethodField()
    current_lon = serializers.SerializerMethodField()
    current_lat = serializers.SerializerMethodField()

    class Meta:
        model = Journey
        fields = [
            "id",
            "origin_lon",
            "origin_lat",
            "destination_lon",
            "destination_lat",
            "status",
            "current_lon",
            "current_lat",
            "distance_remaining_m",
            "eta_seconds",
            "next_turn_instruction",
            "next_turn_distance_m",
            "route_steps",
            "started_at",
            "updated_at",
            "ended_at",
            "client_id",
        ]

    def get_origin_lon(self, obj):
        return obj.origin.x if obj.origin else None

    def get_origin_lat(self, obj):
        return obj.origin.y if obj.origin else None

    def get_destination_lon(self, obj):
        return obj.destination.x if obj.destination else None

    def get_destination_lat(self, obj):
        return obj.destination.y if obj.destination else None

    def get_current_lon(self, obj):
        return obj.current_position.x if obj.current_position else None

    def get_current_lat(self, obj):
        return obj.current_position.y if obj.current_position else None