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
