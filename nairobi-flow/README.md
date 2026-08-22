# NAIROBI FLOW

**Nairobi Traffic Intelligence & Predictive Rerouting Platform.**

An open, vendor-neutral traffic intelligence platform for the Nairobi
metropolitan area. The system observes traffic, estimates the current
network state, predicts short-term evolution, and evaluates routing
strategies before congestion forms.

The intent is a *traffic intelligence layer* for Nairobi, not another
navigation application.

```
OBSERVE → UNDERSTAND → PREDICT → SIMULATE → OPTIMIZE → RECOMMEND → OBSERVE
```

See [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md) for the full brief,
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for component layout, and
[docs/ROADMAP.md](docs/ROADMAP.md) for phased delivery.

## MVP scope

The first MVP is the **Rongai → Nairobi CBD** corridor. The architecture is
built to expand across the metropolitan area, but the first end-to-end
demonstration is deliberately constrained.

## Stack

Open-source only for the runtime path:

- **Map data**: OpenStreetMap, OSMnx
- **Database**: PostgreSQL + PostGIS
- **Routing**: OSRM
- **Simulation**: SUMO
- **Backend**: Django + Django REST Framework, Celery, Redis
- **Data science / ML**: NumPy, Pandas, scikit-learn, PyTorch (only when justified)
- **Computer vision** (future): OpenCV, YOLO
- **Frontend**: React + TypeScript + Vite + Tailwind + MapLibre GL JS
- **Containers**: Docker + Docker Compose

Commercial systems (Google Maps, HERE, Waze, TomTom) may be used for
research, benchmarking, and manual validation, but are never mandatory
runtime dependencies.

## Quick start

```sh
cp .env.example .env
docker compose up --build
```

Services:

| Service   | Port  | Description                               |
|-----------|-------|-------------------------------------------|
| frontend  | 5173  | React + MapLibre dashboard                |
| backend   | 8000  | Django REST API                           |
| postgis   | 5432  | PostgreSQL 16 + PostGIS 3                 |
| redis     | 6379  | Broker / cache for Celery                 |
| osrm      | 5000  | OSRM routing engine (see services/osrm)   |

## Repository layout

```
backend/    Django project + modular apps (network, observations, traffic_state,
            prediction, routing, simulation, api)
frontend/   React + TypeScript + Vite dashboard
services/   Third-party services (OSRM, SUMO) with build/run instructions
scripts/    One-shot data pipeline scripts (OSM extraction, network loading)
data/       Local data (git-ignored) with README describing layout
docs/       Architecture, project brief, roadmap
```

## Principles

- Modular: data sources, state, prediction, routing, optimization, simulation,
  API, and frontend are independently replaceable.
- Reproducible: every experiment records scenario, seed, and configuration.
- Honest: never fabricate metrics. Every reported number traces to an experiment.
- Private: GPS data is aggregated and anonymized; no individual trajectories are
  exposed publicly.
