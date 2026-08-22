"""Road-network models: RoadSegment, Intersection, Corridor.

Follows the brief: distinguish Road / Road Segment / Intersection / Corridor.
Geometry uses SRID 4326 (WGS84); switch to a projected CRS for
length/capacity calculations at query time.
"""
from __future__ import annotations

from django.contrib.gis.db import models


class RoadType(models.TextChoices):
    MOTORWAY = "motorway", "Motorway"
    TRUNK = "trunk", "Trunk"
    PRIMARY = "primary", "Primary"
    SECONDARY = "secondary", "Secondary"
    TERTIARY = "tertiary", "Tertiary"
    RESIDENTIAL = "residential", "Residential"
    SERVICE = "service", "Service"
    UNCLASSIFIED = "unclassified", "Unclassified"
    OTHER = "other", "Other"


class Intersection(models.Model):
    osm_node_id = models.BigIntegerField(unique=True, null=True, blank=True)
    geometry = models.PointField(srid=4326)
    signalized = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["osm_node_id"])]

    def __str__(self) -> str:
        return f"Intersection#{self.pk}"


class RoadSegment(models.Model):
    """One directed segment between two intersections."""

    osm_way_id = models.BigIntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    road_type = models.CharField(
        max_length=32, choices=RoadType.choices, default=RoadType.OTHER
    )
    geometry = models.LineStringField(srid=4326)
    length_m = models.FloatField(help_text="Segment length in metres")
    lanes = models.PositiveSmallIntegerField(null=True, blank=True)
    one_way = models.BooleanField(default=False)
    speed_limit_kmh = models.FloatField(null=True, blank=True)
    free_flow_speed_kmh = models.FloatField(null=True, blank=True)
    capacity_vph = models.FloatField(
        null=True, blank=True, help_text="Estimated capacity in vehicles/hour"
    )
    start_node = models.ForeignKey(
        Intersection,
        related_name="outgoing_segments",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    end_node = models.ForeignKey(
        Intersection,
        related_name="incoming_segments",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["osm_way_id"]),
            models.Index(fields=["road_type"]),
        ]

    def __str__(self) -> str:
        return self.name or f"RoadSegment#{self.pk}"


class Corridor(models.Model):
    """A named sequence of segments (e.g. Rongai → CBD via Lang'ata Road)."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    segments = models.ManyToManyField(
        RoadSegment, through="CorridorSegment", related_name="corridors"
    )

    def __str__(self) -> str:
        return self.name


class CorridorSegment(models.Model):
    corridor = models.ForeignKey(Corridor, on_delete=models.CASCADE)
    segment = models.ForeignKey(RoadSegment, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ("corridor", "order")
        ordering = ["order"]
