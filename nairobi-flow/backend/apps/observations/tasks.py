"""Celery tasks for ingesting and processing traffic observations."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from celery import shared_task
from django.contrib.gis.geos import Point
from django.utils.timezone import make_aware

from apps.observations.mapmatching import map_match_batch
from apps.observations.models import ObservationSource, TrafficObservation

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def ingest_gps_batch(self, observations: list[dict[str, Any]]) -> dict[str, Any]:
    """Ingest a batch of GPS observations with map matching.

    Args:
        observations: List of dicts with keys:
            - timestamp: ISO datetime string
            - latitude: float
            - longitude: float
            - speed_kmh: float (optional)
            - vehicle_count: int (optional)
            - source: str (default "gps")
            - confidence: float (default 1.0)
            - payload: dict (optional)

    Returns:
        Dict with:
            - ingested_count: Number of observations successfully stored
            - failed_count: Number that failed
            - matched_count: Number with successful map matches
    """
    try:
        if not observations:
            return {"ingested_count": 0, "failed_count": 0, "matched_count": 0}

        # Call map-matching service
        matched_observations = map_match_batch(observations)

        ingested = 0
        failed = 0
        matched = 0

        for obs in matched_observations:
            try:
                # Parse timestamp
                timestamp_str = obs.get("timestamp")
                if isinstance(timestamp_str, str):
                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    if timestamp.tzinfo is None:
                        timestamp = make_aware(timestamp)
                else:
                    timestamp = timestamp_str

                # Create Point from lat/lon
                lat = obs.get("latitude")
                lon = obs.get("longitude")
                location = Point(lon, lat, srid=4326) if lat and lon else None

                # Build observation dict
                obs_data = {
                    "timestamp": timestamp,
                    "location": location,
                    "speed_kmh": obs.get("speed_kmh"),
                    "vehicle_count": obs.get("vehicle_count"),
                    "density_vpk": obs.get("density_vpk"),
                    "travel_time_s": obs.get("travel_time_s"),
                    "source": obs.get("source", ObservationSource.GPS),
                    "confidence": obs.get("confidence", 1.0),
                    "payload": obs.get("payload", {}),
                    "matched_segment_id": obs.get("matched_segment_id"),
                    "match_confidence": obs.get("match_confidence"),
                    "raw_lat_lon": obs.get("raw_lat_lon", {}),
                }

                # Upsert observation
                TrafficObservation.objects.update_or_create(
                    timestamp=timestamp,
                    location=location,
                    source=obs_data["source"],
                    defaults=obs_data,
                )
                ingested += 1

                if obs.get("matched_segment_id") is not None:
                    matched += 1

            except Exception as e:
                logger.error(f"Failed to ingest observation: {e}", exc_info=True)
                failed += 1
                continue

        logger.info(
            f"Ingested {ingested} observations, "
            f"{matched} with successful map matches, "
            f"{failed} failed"
        )

        return {
            "ingested_count": ingested,
            "failed_count": failed,
            "matched_count": matched,
        }

    except Exception as exc:
        logger.error(f"Error in ingest_gps_batch: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
