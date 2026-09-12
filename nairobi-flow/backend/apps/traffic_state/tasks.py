"""Celery tasks for traffic state estimation."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.db.models import Avg, Count
from django.utils.timezone import now

from apps.observations.models import TrafficObservation
from apps.traffic_state.models import TrafficSegmentState

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def estimate_traffic_state_by_segment(self, lookback_minutes: int = 5) -> dict:
    """Estimate traffic state by OSM segment from map-matched observations.

    Groups recent TrafficObservation entries by matched_segment_id (OSM way ID),
    filters for high-confidence matches (>= 0.8), and aggregates speed/count data.

    Args:
        lookback_minutes: Look back this many minutes for observations.
                         Default 5 minutes (typical traffic window).

    Returns:
        Dict with:
            - segments_processed: Number of unique segments with observations
            - states_created: Number of TrafficSegmentState records written
            - failed_count: Number of failures
    """
    try:
        cutoff = now() - timedelta(minutes=lookback_minutes)

        # Get all high-confidence matched observations from the lookback window
        observations = TrafficObservation.objects.filter(
            timestamp__gte=cutoff,
            matched_segment_id__isnull=False,
            match_confidence__gte=0.8,
        ).exclude(speed_kmh__isnull=True)

        if not observations.exists():
            logger.info(f"No high-confidence observations in last {lookback_minutes} minutes")
            return {
                "segments_processed": 0,
                "states_created": 0,
                "failed_count": 0,
            }

        # Aggregate by segment_id and timestamp (current time)
        aggregated = observations.values("matched_segment_id").annotate(
            avg_speed=Avg("speed_kmh"),
            vehicle_count=Count("id"),
            mean_confidence=Avg("match_confidence"),
        )

        segments_processed = len(aggregated)
        states_created = 0
        failed_count = 0

        for agg in aggregated:
            try:
                segment_id = agg["matched_segment_id"]
                avg_speed = agg["avg_speed"]
                vehicle_count = agg["vehicle_count"]
                mean_confidence = agg["mean_confidence"]

                # Create or update segment state for the current timestamp
                TrafficSegmentState.objects.update_or_create(
                    segment_id=segment_id,
                    timestamp=now(),
                    defaults={
                        "avg_speed_kmh": float(avg_speed) if avg_speed else None,
                        "vehicle_count": int(vehicle_count) if vehicle_count else None,
                        "confidence": float(mean_confidence) if mean_confidence else 0.0,
                        "observation_count": vehicle_count,
                    },
                )
                states_created += 1

            except Exception as e:
                logger.error(
                    f"Failed to create state for segment {agg.get('matched_segment_id')}: {e}",
                    exc_info=True,
                )
                failed_count += 1
                continue

        logger.info(
            f"Processed {segments_processed} segments, "
            f"created {states_created} states, "
            f"{failed_count} failed"
        )

        return {
            "segments_processed": segments_processed,
            "states_created": states_created,
            "failed_count": failed_count,
        }

    except Exception as exc:
        logger.error(f"Error in estimate_traffic_state_by_segment: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
