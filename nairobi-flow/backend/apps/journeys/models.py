"""Journey and live navigation models."""

from __future__ import annotations

from django.contrib.gis.db import models
from django.utils import timezone


class Journey(models.Model):
    """A single navigation session: start → active → paused/completed.

    A journey is personal and consent-gated. It is conceptually
    separate from a network-wide traffic observation, though eligible
    GPS samples may feed back into the traffic model after aggregation
    and anonymisation.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.CharField(max_length=64, primary_key=True)
    origin = models.PointField(srid=4326)
    destination = models.PointField(srid=4326)
    selected_route_geometry = models.LineStringField(srid=4326, null=True, blank=True)
    selected_route_distance_m = models.FloatField(null=True, blank=True)
    selected_route_duration_s = models.FloatField(null=True, blank=True)
    route_steps = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ACTIVE
    )
    current_position = models.PointField(srid=4326, null=True, blank=True)
    distance_remaining_m = models.FloatField(null=True, blank=True)
    eta_seconds = models.IntegerField(null=True, blank=True)
    next_turn_instruction = models.CharField(max_length=256, blank=True, default="")
    next_turn_distance_m = models.FloatField(null=True, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    client_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"Journey {self.id} ({self.status})"


class JourneyLocation(models.Model):
    """Raw GPS sample for a journey, used for map matching and progress."""

    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="locations"
    )
    position = models.PointField(srid=4326)
    speed_kmh = models.FloatField(null=True, blank=True)
    heading_deg = models.FloatField(null=True, blank=True)
    accuracy_m = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.journey_id} @ {self.timestamp.isoformat()}"