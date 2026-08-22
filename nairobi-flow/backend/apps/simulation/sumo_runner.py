"""SUMO simulation runner (stub).

Wraps `sumo` / `sumo-gui` invocation for scenario runs. Real integration
lives in `services/sumo/` where the .sumocfg and network files reside.
Here we only shell out and record metrics into `TrafficSimulation`.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SumoRunConfig:
    sumocfg: Path
    seed: int
    end_time_s: float
    binary: str = "sumo"  # or "sumo-gui"

    def as_command(self) -> list[str]:
        return [
            self.binary,
            "-c", str(self.sumocfg),
            "--seed", str(self.seed),
            "--end", str(self.end_time_s),
            "--no-step-log", "true",
            "--time-to-teleport", "-1",
        ]


def run(config: SumoRunConfig) -> subprocess.CompletedProcess:
    """Run SUMO synchronously and return the completed process."""
    return subprocess.run(config.as_command(), check=True, capture_output=True, text=True)
