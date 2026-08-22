# SUMO

SUMO (Simulation of Urban MObility) provides the initial source of
traffic data for NAIROBI FLOW. This directory holds scenarios,
network conversions, and demand definitions.

## Prerequisites

Install SUMO locally (Docker image is used for CI; local install for
`sumo-gui` iteration):

```sh
brew install sumo               # macOS
sudo apt install sumo sumo-tools sumo-doc  # Debian/Ubuntu
```

Set `SUMO_HOME` in your `.env` (defaults to `/usr/share/sumo`).

## Converting OSM → SUMO network

After running `scripts/extract_osm.py` you have an OSM/GraphML network.
Convert to SUMO's `.net.xml`:

```sh
netconvert \
  --osm-files data/osm/rongai.osm \
  --output-file services/sumo/scenarios/rongai/network.net.xml \
  --geometry.remove --roundabouts.guess --ramps.guess \
  --junctions.join --tls.guess-signals --tls.discard-simple --tls.join
```

## Scenarios

Each scenario lives under `scenarios/<name>/` with:

```
scenarios/
  rongai_morning_normal/
    network.net.xml
    demand.rou.xml
    config.sumocfg
    additional.add.xml   # detectors, TLS overrides, etc.
```

Scenarios must be **reproducible**: the same `.sumocfg` + `--seed` gives
identical output. Every simulation run is recorded in the
`TrafficSimulation` table with its scenario, seed, strategy, and metrics.

## Named scenarios (brief §15)

`NORMAL_MORNING`, `HEAVY_MORNING`, `NORMAL_EVENING`, `HEAVY_EVENING`,
`RAIN`, `ACCIDENT`, `ROAD_CLOSURE`, `EVENT`, `INCREASED_DEMAND`.

## Do not

- Do not attempt physical traffic-signal control from these scenarios.
- Do not fabricate demand numbers — document the source of every
  origin/destination volume.
