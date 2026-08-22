"""SUMO-based observation source.

Reads simulation output (FCD, edge-data, or live TraCI) and yields
`TrafficObservationRecord`s. The MVP uses batch FCD output from a
completed SUMO run; TraCI streaming is added when the simulation
engine matures.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

from .base import TrafficDataSource, TrafficObservationRecord


@dataclass
class SUMOSource(TrafficDataSource):
    """Parses a SUMO FCD (floating-car data) XML file."""

    fcd_path: Path
    simulation_start: datetime
    source_name: str = "sumo"

    def stream(self) -> Iterable[TrafficObservationRecord]:
        for _event, elem in ET.iterparse(self.fcd_path, events=("end",)):
            if elem.tag != "timestep":
                continue
            sim_time_s = float(elem.get("time", 0.0))
            ts = self.simulation_start + timedelta(seconds=sim_time_s)
            for veh in elem.findall("vehicle"):
                yield TrafficObservationRecord(
                    timestamp=ts,
                    latitude=float(veh.get("y")) if veh.get("y") else None,
                    longitude=float(veh.get("x")) if veh.get("x") else None,
                    speed_kmh=_ms_to_kmh(veh.get("speed")),
                    source=self.source_name,
                    payload={
                        "vehicle_id": veh.get("id"),
                        "edge": veh.get("lane", "").rsplit("_", 1)[0] or None,
                    },
                )
            elem.clear()


def _ms_to_kmh(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value) * 3.6
    except ValueError:
        return None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)
