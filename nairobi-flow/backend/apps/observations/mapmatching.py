"""Map matching service for GPS observations to OSM road segments.

Uses OSRM (Open Source Routing Machine) /match endpoint to snap GPS traces
to the road network and extract segment IDs and confidence scores.
"""
from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

OSRM_BASE_URL = "http://router.project-osrm.org"
OSRM_MATCH_ENDPOINT = f"{OSRM_BASE_URL}/match/v1/driving"

MIN_CONFIDENCE_THRESHOLD = 0.8
BATCH_SIZE = 500


def map_match_batch(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map-match a batch of GPS observations to OSM way IDs.

    Args:
        observations: List of dicts with keys:
            - latitude: float
            - longitude: float
            - timestamp: ISO datetime string
            - (optional) speed_kmh, etc.

    Returns:
        List of enriched observation dicts with keys:
            - matched_segment_id: int OSM way ID (null if no match)
            - match_confidence: float 0.0-1.0 (null if no match)
            - (all original keys preserved)

    If OSRM is unavailable, logs warning and returns observations
    with null matched_segment_id and match_confidence.
    """
    if not observations:
        return []

    result = []

    try:
        for batch in _chunk(observations, BATCH_SIZE):
            matched = _match_batch_with_osrm(batch)
            result.extend(matched)
    except Exception as e:
        logger.warning(
            f"Map matching service unavailable: {e}. "
            f"Returning {len(observations)} observations with null match fields."
        )
        for obs in observations:
            obs.setdefault("matched_segment_id", None)
            obs.setdefault("match_confidence", None)
            result.append(obs)

    return result


def _match_batch_with_osrm(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Call OSRM /match endpoint for a single batch."""

    coords = ";".join(
        f"{obs['longitude']},{obs['latitude']}" for obs in observations
    )

    try:
        response = requests.get(
            OSRM_MATCH_ENDPOINT,
            params={
                "coordinates": coords,
                "overview": "full",
                "geometries": "geojson",
            },
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"OSRM request failed: {e}")
        raise

    data = response.json()

    if data.get("code") != "Ok":
        logger.warning(f"OSRM returned non-OK code: {data.get('code', 'unknown')}")
        for obs in observations:
            obs.setdefault("matched_segment_id", None)
            obs.setdefault("match_confidence", None)
        return observations

    matchings = data.get("matchings", [])

    for i, obs in enumerate(observations):
        if i < len(matchings):
            matching = matchings[i]
            confidence = matching.get("confidence", 0.0)

            if confidence >= MIN_CONFIDENCE_THRESHOLD:
                way_id = _extract_way_id(matching)
                obs["matched_segment_id"] = way_id
                obs["match_confidence"] = float(confidence)
            else:
                obs["matched_segment_id"] = None
                obs["match_confidence"] = float(confidence)
        else:
            obs["matched_segment_id"] = None
            obs["match_confidence"] = None

        if "latitude" in obs and "longitude" in obs:
            obs.setdefault("raw_lat_lon", {
                "latitude": obs["latitude"],
                "longitude": obs["longitude"],
            })

    return observations


def _extract_way_id(matching: dict[str, Any]) -> int | None:
    """Extract OSM way ID from OSRM matching result.

    OSRM returns metadata about each match in the 'legs' and 'steps'
    structure. We extract the first way ID found.
    """
    legs = matching.get("legs", [])
    for leg in legs:
        steps = leg.get("steps", [])
        for step in steps:
            if "way_name" in step:
                try:
                    return int(step["way_name"])
                except (ValueError, TypeError):
                    pass

    return None


def _chunk(lst: list, chunk_size: int) -> list[list]:
    """Split list into chunks of specified size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]
