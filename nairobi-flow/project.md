# Nairobi Flow — Project Description & Tech Stack

Nairobi Traffic Intelligence & Predictive Rerouting Platform.

An open, vendor-neutral traffic intelligence platform for the Nairobi
metropolitan area. The system observes traffic, estimates the current
state of the road network, predicts short-term evolution, evaluates routing
strategies before congestion forms, and recommends or eventually optimizes
vehicle routing.

The intent is a **traffic intelligence layer** for Nairobi, not another
navigation application.

```
OBSERVE → UNDERSTAND → PREDICT → SIMULATE → OPTIMIZE → RECOMMEND → OBSERVE
```

---

## 1. Project vision

Build an intelligent transportation system (ITS) for Nairobi, Kenya that can:

- Observe traffic from GPS probes, authorized cameras, manual counts, and open
  data sources.
- Estimate the current state of the road network (speed, density, congestion
  level per segment).
- Predict how traffic will evolve over 5 / 10 / 15 / 30-minute horizons.
- Recommend routes using predicted state at the time a vehicle actually
  reaches each segment — not just current conditions.
- Optimize total network travel time through iterative, network-aware
  assignment.
- Simulate scenarios (normal/heavy morning/evening, rain, accident, road
  closure, event, increased demand) and measure outcomes.

The long-term objective is a traffic intelligence layer for Nairobi capable
of functioning independently using OpenStreetMap, SUMO, OSRM, PostGIS, GPS
observations, authorized CV observations, manual counts, legal public
datasets, and simulated data.

---

## 2. Core problem

Nairobi experiences severe congestion during peak periods. The problem is
not simply the lack of roads — Nairobi has multiple corridors connecting the
same origins and destinations.

Traditional navigation finds a currently efficient route, but if a large
number of vehicles are simultaneously given the same route, that route itself
becomes congested. The project therefore investigates:

- What route is likely to be optimal when the vehicle actually reaches that
  part of the network?
- How should vehicles be distributed across the network to minimize overall
  congestion and total travel time?

---

## 3. Central research question

Can short-term traffic prediction combined with network-aware routing reduce
congestion and total travel time across Nairobi's road network?

The system experimentally compares:

1. Conventional / current-condition routing
2. Predictive routing
3. Network-aware predictive routing

---

## 4. Current state

The system is running as a **mobile-first web application**:

- **Full-screen map** as background (MapLibre GL JS)
- **Floating top bar**: hamburger menu, "Where to?" search bar, profile icon
- **Collapsible bottom sheet**: origin/destination inputs with pin icons,
  swap button, departure time, strategy dropdown, "Recommend Routes" CTA
- **Route cards**: tappable cards showing time/distance/risk, "Start Drive"
  button
- **Floating map controls**: current-location button and report button
- **Any origin, any destination**: tap the map or type coordinates. The old
  Rongai → CBD preset has been removed.
- **OSRM failover**: local OSRM container tried first, public OSRM API
  (`router.project-osrm.org`) as fallback

Geographic scope: MVP focus on Nairobi metropolitan area, starting with the
**Rongai → Nairobi CBD** corridor. Architecture supports expansion across the
metropolitan area.

---

## 5. Geographic scope

**MVP focus:** Nairobi metropolitan area, starting with the **Rongai →
Nairobi CBD** corridor. The architecture is built to expand across the
metropolitan area — Lang'ata, Ngong, Karen, Kikuyu, Kiambu, Thika, Mombasa
Road, Waiyaki Way, Westlands, Eastlands, CBD, and beyond — but the first
end-to-end demonstration is deliberately constrained to one corridor.

---

## 6. How we work (engineering & development philosophy)

### Modularity
Data sources, traffic state, prediction, routing, optimization, simulation,
API, and frontend are independently replaceable. No stage depends on a
specific provider. New data sources are added by subclassing the
`TrafficDataSource` ABC; new predictors implement `BasePredictor`; routing
strategies (`ConventionalRouting`, `PredictiveRouting`, `NetworkAwareRouting`)
all share a `RoutingStrategy` interface.

### Reproducible experiments
Every experiment records `scenario_id`, configuration, seed, simulation time,
routing strategy, and results. No performance number is ever fabricated;
every reported metric traces to an experiment.

### Baselines first, ML only when justified
Prediction starts simple (historical average, moving average, linear
regression). ML models (Random Forest, Gradient Boosting, XGBoost, LSTM, GRU,
temporal NNs) are added only when they measurably beat baselines on held-out
data. PyTorch is used only when justified.

### Open-source runtime
Open-source only for the runtime path. Commercial systems (Google Maps, HERE,
Waze, TomTom) may be used for research, benchmarking, and manual validation,
but are never mandatory runtime dependencies.

### Reliability & graceful degradation
- Prediction unavailable → historical model.
- Historical model unavailable → current-condition routing.
- OSRM unavailable → public OSRM API fallback.
The system never stops functioning because one source failed.

### Data validation & privacy
- GPS data is aggregated and anonymized; no individual trajectories are
  exposed publicly.
- Separate identity from trajectories; no unnecessary PII.
- Incidents (accidents, closures, construction, flooding, stalls, events,
  police control) modify capacity, speed, availability, and demand.
- Weather is optional and only kept if it improves accuracy.
- Traffic signal control is not attempted in v1.
- KURA/government integration is via a generic interface, never a hard
  dependency.

---

## 7. How the system is built (architecture)

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
REACT + MAPLIBRE DASHBOARD (mobile-first)
```

Real-time flow:

```
GPS/Cameras → ingest → validate → map-match → aggregate → state →
prediction → route eval → recommendation
```

### Data flow

1. **Ingestion** — Observations arrive through pluggable `TrafficDataSource`
   implementations (`SUMOSource`, `GPSSource`, `CameraSource`,
   `ManualCountSource`, `PublicDatasetSource`, `GovernmentSource`,
   `ExternalBenchmarkSource`). Each yields a `TrafficObservation` with the
   schema:

   ```
   road_id, timestamp, latitude, longitude,
   speed, vehicle_count, density, travel_time, source, confidence
   ```

2. **Storage** — PostGIS stores road segments, intersections, corridors,
   observations, states, predictions, simulations, scenarios, routes,
   incidents, weather, metrics, and model versions.

3. **Traffic state** — Per segment: speed (avg/median), vehicle count,
   density, travel time, queue length, occupancy, congestion level,
   confidence. State classes: `FREE_FLOW`, `LIGHT`, `MODERATE`, `HEAVY`,
   `SEVERE`. Congestion ratio:

   ```
   congestion_ratio = current_speed / free_flow_speed
   ```

4. **Prediction** — Horizons of 5, 10, 15, 30 minutes; targets: future speed,
   travel time, congestion level, queue length. Baselines first; ML models
   evaluated on MAE, RMSE, MAPE, inference time, and training time.

5. **Routing** — OSRM generates candidate routes. The traffic intelligence
   layer scores them using predicted state at arrival time. Three strategies
   are compared: conventional (current-condition), predictive, and
   network-aware predictive (recalculating future travel time when many
   vehicles are redirected onto the same alternative).

6. **Simulation** — SUMO models the Nairobi network with origin–destination
   demand between zones. Every scenario is reproducible with
   `scenario_id`, configuration, seed, simulation time, routing strategy, and
   results. Named scenarios: `NORMAL_MORNING`, `HEAVY_MORNING`,
   `NORMAL_EVENING`, `HEAVY_EVENING`, `RAIN`, `ACCIDENT`, `ROAD_CLOSURE`,
   `EVENT`, `INCREASED_DEMAND`.

7. **API** — Django REST Framework exposes roads, corridors, current/history/
   predictions, route recommendations, incidents, simulations, metrics, and
   models. Metrics endpoint: `/api/metrics/`.

8. **Frontend** — React + TypeScript + MapLibre GL JS mobile-first dashboard
   with Live Traffic, Prediction, Route Recommendation, Simulation, Network
   Metrics, and Historical Analysis views.

---

## 8. Tech stack

### Backend (Django)
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Web framework | Django 5.x | Web application & ORM |
| API | Django REST Framework | REST API & viewsets |
| API docs | drf-spectacular | OpenAPI schema generation |
| CORS | django-cors-headers | Cross-origin resource sharing |
| Filtering | django-filter | Query filtering |
| Background jobs | Celery | Distributed task queue |
| Broker / cache | Redis | Celery broker and cache |
| Database driver | psycopg[binary] | PostgreSQL client |
| Monitoring | django-prometheus, prometheus-client, python-logging-loki | Metrics & Loki logging |
| Env config | python-dotenv | Environment variable loading |
| HTTP | requests, httpx | HTTP clients |
| Testing | pytest, pytest-django | Unit & integration tests |

### Geospatial & data
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Map data | OpenStreetMap via OSMnx | Road network extraction |
| Geospatial | GeoPandas, Shapely, GDAL, pyproj, networkx | Vector geometries, spatial analysis, projections, graph algorithms |
| Database | PostgreSQL 16 + PostGIS 3 | Spatial database |
| Data science | NumPy, Pandas, scikit-learn, scipy | Numerical computing, dataframes, ML baselines |
| Deep learning | PyTorch (only when justified) | Neural networks |

### Routing & simulation
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Routing engine | OSRM | Candidate route generation |
| Traffic simulation | SUMO | Microscopic traffic simulation |

### Frontend
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | React 18 + TypeScript | UI application |
| Build tool | Vite | Dev server & bundling |
| Styling | Tailwind CSS | Utility-first CSS |
| Map rendering | MapLibre GL JS | Interactive map visualization |
| Geo types | @types/geojson | GeoJSON TypeScript types |

### Infrastructure & observability
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Containers | Docker + Docker Compose | Service orchestration |
| Metrics collection | Prometheus | Time-series metrics |
| Visualization | Grafana | Dashboards |
| Log aggregation | Loki | Log storage & querying |
| DB metrics | postgres_exporter | PostgreSQL metrics |
| VCS | Git, GitHub | Version control |

---

## 9. Repository layout

```
backend/       Django project + modular apps (network, observations,
               traffic_state, prediction, routing, simulation, api)
frontend/      React + TypeScript + Vite mobile-first dashboard
services/      Third-party services (OSRM, SUMO) with build/run instructions
scripts/       One-shot data pipeline scripts (OSM extraction,
               network loading)
data/          Local data (git-ignored) with README describing layout
docs/          Architecture, project brief, roadmap
monitoring/    Prometheus, Grafana, Loki configuration
```

### Backend Django apps

| App | Responsibility |
|-----|----------------|
| `network` | Road segments, intersections, corridors (PostGIS geometries) |
| `observations` | Traffic observations + pluggable `TrafficDataSource` interface |
| `traffic_state` | Estimation of current per-segment state |
| `prediction` | Baseline + ML predictors and their evaluations |
| `routing` | OSRM client, routing strategies (conventional / predictive / net-aware) |
| `simulation` | SUMO scenarios, runs, and stored vehicle traces |
| `api` | DRF viewsets and URL wiring |

---

## 10. Services (Docker Compose)

| Service | Port | Description |
|---------|------|-------------|
| postgis | 5432 (5433 host) | PostgreSQL 16 + PostGIS 3 |
| redis | 6379 (6380 host) | Celery broker / cache |
| backend | 8000 | Django REST API |
| celery | — | Celery worker |
| frontend | 5173 | React + MapLibre mobile-first dashboard |
| osrm | 5000 | OSRM routing engine (routing profile) |
| prometheus | 9090 | Metrics collection |
| grafana | 3000 | Dashboards |
| loki | 3100 | Log aggregation |
| postgres_exporter | 9187 | PostgreSQL metrics |

Host ports for postgis and redis are overridden (`5433:5432`, `6380:6379`)
because 5432/6379 are occupied by unrelated local services. Containers still
communicate with each other on 5432/6379 inside the Docker network.

---

## 11. MVP definition

The MVP succeeds when this pipeline runs end-to-end for the **Rongai →
Nairobi CBD** corridor:

```
OSM → OSMnx → PostGIS → SUMO → traffic state → prediction →
OSRM candidates → predictive selection → SUMO re-simulation →
comparison → MapLibre dashboard
```

First demonstration answers: *what happens if we know congestion is about to
develop on the currently fastest route?*

Only report numbers produced by the experiment. Never fabricate traffic data
or performance improvements.

---

## 12. Development phases

| Phase | Name | Outcome |
|-------|------|---------|
| 0 | Research | Notes on Nairobi patterns and comparable ITS systems |
| 1 | Road network | OSM → OSMnx → PostGIS graph for Nairobi (Rongai corridor) |
| 2 | Routing | OSRM deployed, candidate routes API (with public fallback) |
| 3 | Traffic simulation | SUMO network + realistic demand for peak scenarios |
| 4 | Data platform | Observation, state, and prediction pipelines |
| 5 | Prediction | Baselines then ML at 5/10/15/30 min horizons |
| 6 | Predictive routing | Arrival-time-aware route scoring |
| 7 | Network optimization | Iterative traffic assignment; total-network metrics |
| 8 | Dashboard | MapLibre/React UI with live + predicted layers |
| 9 | Real data | GPS probes, authorized cameras, manual counts, open data |
| 10 | Calibration | Simulation vs. observed vs. commercial systems |
| 11 | Pilot | Small consenting user group; measured outcomes |

---

## 13. Constraints — do not

- Fabricate traffic data or performance improvements.
- Assume all roads behave identically.
- Assume drivers always follow recommendations.
- Assume the currently fastest route stays fastest.
- Assume deep learning is automatically superior.
- Make Google / HERE APIs mandatory.
- Build the entire system as a monolith.
- Over-engineer the MVP with Kubernetes / microservices.
- Deploy traffic-signal control in v1.

---

## 14. Quick start

```sh
cp .env.example .env
docker compose up --build
```

OSRM runs under the `routing` profile:

```sh
bash scripts/build_osrm.sh
docker compose --profile routing up osrm
```

Observability stack:

```sh
docker compose up -d prometheus grafana loki postgres_exporter
```

OSRM failover: if the local OSRM container is unavailable, the backend
automatically falls back to the public OSRM API
(`router.project-osrm.org`), so route recommendations work without building
the OSRM graph.