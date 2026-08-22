from __future__ import annotations

from django.contrib.gis.db import models

from apps.network.models import RoadSegment


class ObservationSource(models.TextChoices):
    SUMO = "sumo", "SUMO simulation"
    GPS = "gps", "GPS probe"
    CAMERA = "camera", "Camera / CV"
    MANUAL = "manual", "Manual count"
    PUBLIC = "public", "Public dataset"
    GOVERNMENT = "government", "Government feed"
    EXTERNAL_BENCHMARK = "external_benchmark", "External benchmark"


class TrafficObservation(models.Model):
    """Single traffic observation aligned to a road segment.

    Fields follow the canonical schema in the project brief. `road` may
    be null for raw observations awaiting map-matching.
    """

    road = models.ForeignKey(
        RoadSegment,
        on_delete=models.CASCADE,
        related_name="observations",
        null=True,
        blank=True,
    )
    timestamp = models.DateTimeField(db_index=True)
    location = models.PointField(srid=4326, null=True, blank=True)

    speed_kmh = models.FloatField(null=True, blank=True)
    vehicle_count = models.IntegerField(null=True, blank=True)
    density_vpk = models.FloatField(
        null=True, blank=True, help_text="Vehicles per kilometre"
    )
    travel_time_s = models.FloatField(null=True, blank=True)

    source = models.CharField(max_length=32, choices=ObservationSource.choices)
    confidence = models.FloatField(default=1.0)
    payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["road", "timestamp"]),
            models.Index(fields=["source", "timestamp"]),
        ]
        ordering = ["-timestamp"]
