from __future__ import annotations

from django.db import models

from apps.routing.models import Strategy


class ScenarioName(models.TextChoices):
    NORMAL_MORNING = "normal_morning", "Normal morning"
    HEAVY_MORNING = "heavy_morning", "Heavy morning"
    NORMAL_EVENING = "normal_evening", "Normal evening"
    HEAVY_EVENING = "heavy_evening", "Heavy evening"
    RAIN = "rain", "Rain"
    ACCIDENT = "accident", "Accident"
    ROAD_CLOSURE = "road_closure", "Road closure"
    EVENT = "event", "Event"
    INCREASED_DEMAND = "increased_demand", "Increased demand"


class TrafficScenario(models.Model):
    name = models.CharField(max_length=64, choices=ScenarioName.choices)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.get_name_display()


class TrafficSimulation(models.Model):
    """A single reproducible simulation run."""

    scenario = models.ForeignKey(
        TrafficScenario, on_delete=models.PROTECT, related_name="runs"
    )
    routing_strategy = models.CharField(
        max_length=32, choices=Strategy.choices, default=Strategy.CONVENTIONAL
    )
    random_seed = models.IntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    duration_s = models.FloatField(null=True, blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    artifact_path = models.CharField(max_length=500, blank=True)

    class Meta:
        indexes = [models.Index(fields=["scenario", "routing_strategy"])]


class SimulationVehicle(models.Model):
    simulation = models.ForeignKey(
        TrafficSimulation, on_delete=models.CASCADE, related_name="vehicles"
    )
    vehicle_id = models.CharField(max_length=64)
    origin_zone = models.CharField(max_length=64)
    destination_zone = models.CharField(max_length=64)
    departure_s = models.FloatField()
    arrival_s = models.FloatField(null=True, blank=True)
    travel_time_s = models.FloatField(null=True, blank=True)
    distance_m = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("simulation", "vehicle_id")
