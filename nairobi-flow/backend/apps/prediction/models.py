from __future__ import annotations

from django.db import models

from apps.network.models import RoadSegment


class ModelVersion(models.Model):
    """A trained predictor version. Every prediction references one."""

    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    algorithm = models.CharField(max_length=100)
    trained_at = models.DateTimeField(auto_now_add=True)
    params = models.JSONField(default=dict, blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    artifact_path = models.CharField(max_length=500, blank=True)

    class Meta:
        unique_together = ("name", "version")

    def __str__(self) -> str:
        return f"{self.name}@{self.version}"


class TrafficPrediction(models.Model):
    """Predicted future traffic on a segment at a target time."""

    road = models.ForeignKey(
        RoadSegment, on_delete=models.CASCADE, related_name="predictions"
    )
    made_at = models.DateTimeField(auto_now_add=True, db_index=True)
    target_time = models.DateTimeField(db_index=True)
    horizon_minutes = models.PositiveSmallIntegerField()

    predicted_speed_kmh = models.FloatField(null=True, blank=True)
    predicted_travel_time_s = models.FloatField(null=True, blank=True)
    predicted_congestion_ratio = models.FloatField(null=True, blank=True)
    confidence = models.FloatField(default=1.0)

    model_version = models.ForeignKey(
        ModelVersion, on_delete=models.PROTECT, related_name="predictions"
    )

    class Meta:
        indexes = [
            models.Index(fields=["road", "target_time"]),
            models.Index(fields=["model_version", "made_at"]),
        ]


class PredictionResult(models.Model):
    """Post-hoc evaluation: predicted vs observed."""

    prediction = models.OneToOneField(
        TrafficPrediction, on_delete=models.CASCADE, related_name="result"
    )
    observed_speed_kmh = models.FloatField(null=True, blank=True)
    observed_travel_time_s = models.FloatField(null=True, blank=True)
    absolute_error = models.FloatField(null=True, blank=True)
    squared_error = models.FloatField(null=True, blank=True)
    percent_error = models.FloatField(null=True, blank=True)
