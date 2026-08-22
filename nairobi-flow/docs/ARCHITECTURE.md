# Architecture

The system is a modular pipeline. Each stage can be replaced independently.

```
DATA SOURCES  (SUMO, GPS, Cameras, Manual counts, External benchmarks)
     ↓
INGESTION    (validation, map matching)
     ↓
POSTGIS      (road segments, observations, states, predictions)
     ↓
TRAFFIC STATE ENGINE    → estimates current speed, density, congestion
     ↓
PREDICTION ENGINE       → 5 / 10 / 15 / 30-minute horizons
     ↓
ROUTING (OSRM candidates + predictive scoring)
     ↓
NETWORK OPTIMIZER (iterative assignment, future)
     ↓
DJANGO REST API
     ↓
REACT + MAPLIBRE DASHBOARD
```

## Django apps (backend/apps)

| App               | Responsibility                                                 |
|-------------------|----------------------------------------------------------------|
| `network`         | Road segments, intersections, corridors (PostGIS geometries)   |
| `observations`    | Traffic observations + pluggable `TrafficDataSource` interface |
| `traffic_state`   | Estimation of current per-segment state                        |
| `prediction`      | Baseline + ML predictors and their evaluations                 |
| `routing`         | OSRM client, routing strategies (conventional/predictive/net-aware) |
| `simulation`      | SUMO scenarios, runs, and stored vehicle traces                |
| `api`             | DRF viewsets and URL wiring                                    |

## Data-source contract

All ingestion goes through the `TrafficDataSource` ABC in
`backend/apps/observations/sources/base.py`. Every source yields
`TrafficObservation` records with a common schema:

```
road_id, timestamp, latitude, longitude,
speed, vehicle_count, density, travel_time,
source, confidence
```

New sources (public datasets, KURA feeds, phone probes) are added by
subclassing `TrafficDataSource`. Nothing downstream depends on a
specific provider.

## Prediction contract

Predictors implement `BasePredictor.predict(segment_id, horizon_minutes)` and
return a `PredictionResult`. Baselines (historical average, moving average)
are the starting point; ML models are added only when they measurably beat
the baselines on held-out data.

## Routing strategies

`ConventionalRouting`, `PredictiveRouting`, and `NetworkAwareRouting` all
implement the same `RoutingStrategy` interface so they can be swapped
inside experiments while keeping the demand, seed, and network fixed.

## Reliability fallbacks

- Prediction unavailable → historical model
- Historical model unavailable → current-condition routing
- OSRM unavailable → cached last-known routes for the corridor

The system never stops functioning because one source failed.
