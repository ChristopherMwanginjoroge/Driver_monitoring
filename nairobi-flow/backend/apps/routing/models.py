from __future__ import annotations

from django.contrib.gis.db import models


class Strategy(models.TextChoices):
    CONVENTIONAL = "conventional", "Conventional (current-condition)"
    PREDICTIVE = "predictive", "Predictive"
    NETWORK_AWARE = "network_aware", "Network-aware predictive"


class RouteRequest(models.Model):
    origin = models.PointField(srid=4326)
    destination = models.PointField(srid=4326)
    departure_time = models.DateTimeField()
    requested_at = models.DateTimeField(auto_now_add=True)
    strategy = models.CharField(
        max_length=32, choices=Strategy.choices, default=Strategy.CONVENTIONAL
    )
    client_id = models.CharField(max_length=64, blank=True)


class RouteRecommendation(models.Model):
    request = models.ForeignKey(
        RouteRequest, on_delete=models.CASCADE, related_name="recommendations"
    )
    rank = models.PositiveSmallIntegerField()
    geometry = models.LineStringField(srid=4326)
    current_travel_time_s = models.FloatField(null=True, blank=True)
    predicted_travel_time_s = models.FloatField(null=True, blank=True)
    risk_level = models.CharField(max_length=16, blank=True)
    strategy = models.CharField(
        max_length=32, choices=Strategy.choices, default=Strategy.CONVENTIONAL
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["request", "rank"]
