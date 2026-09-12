from __future__ import annotations

from django.db import models

from apps.network.models import RoadSegment


class CongestionLevel(models.TextChoices):
    FREE_FLOW = "free_flow", "Free flow"
    LIGHT = "light", "Light"
    MODERATE = "moderate", "Moderate"
    HEAVY = "heavy", "Heavy"
    SEVERE = "severe", "Severe"


class TrafficState(models.Model):
    """Aggregated state for a segment over a time window."""

    road = models.ForeignKey(
        RoadSegment, on_delete=models.CASCADE, related_name="states"
    )
    window_start = models.DateTimeField(db_index=True)
    window_end = models.DateTimeField()

    avg_speed_kmh = models.FloatField(null=True, blank=True)
    median_speed_kmh = models.FloatField(null=True, blank=True)
    vehicle_count = models.IntegerField(null=True, blank=True)
    density_vpk = models.FloatField(null=True, blank=True)
    travel_time_s = models.FloatField(null=True, blank=True)
    queue_length_m = models.FloatField(null=True, blank=True)
    congestion_ratio = models.FloatField(
        null=True, blank=True, help_text="current_speed / free_flow_speed"
    )
    congestion_level = models.CharField(
        max_length=16,
        choices=CongestionLevel.choices,
        default=CongestionLevel.FREE_FLOW,
    )
    confidence = models.FloatField(default=1.0)
    observation_count = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["road", "window_start"]),
        ]
        unique_together = ("road", "window_start")


class TrafficSegmentState(models.Model):
    """Segment-level traffic state derived from map-matched observations.

    Aggregates observations grouped by OSM way ID (matched_segment_id)
    rather than RoadSegment FK. Enables tracking of traffic flow on
    unmapped or partially mapped segments.
    """

    segment_id = models.IntegerField(db_index=True, help_text="OSM way ID")
    timestamp = models.DateTimeField(db_index=True)

    avg_speed_kmh = models.FloatField(null=True, blank=True)
    vehicle_count = models.PositiveIntegerField(null=True, blank=True)
    confidence = models.FloatField(
        default=0.0, help_text="Mean confidence of matched observations"
    )
    observation_count = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["segment_id", "timestamp"]),
        ]
        unique_together = ("segment_id", "timestamp")
