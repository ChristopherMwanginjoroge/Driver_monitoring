# PROJECT BRIEF

The canonical project brief for **NAIROBI FLOW** — Nairobi Traffic
Intelligence & Predictive Rerouting Platform.

> This document is the source of truth for scope, constraints, and
> philosophy. When implementation choices conflict with the brief,
> the brief wins.

---

## 1. Project vision

Build an intelligent transportation system for Nairobi, Kenya that can
observe traffic, understand the current state of the road network,
predict how traffic will evolve, and recommend or eventually optimize
vehicle routing before congestion becomes severe.

The long-term objective is to create a *traffic intelligence layer* for
Nairobi rather than simply another navigation application.

```
TRAFFIC MONITORING
        ↓
TRAFFIC STATE ESTIMATION
        ↓
TRAFFIC PREDICTION
        ↓
PREDICTIVE REROUTING
        ↓
NETWORK OPTIMIZATION
        ↓
INTELLIGENT TRAFFIC MANAGEMENT
```

## 2. Core problem

Nairobi experiences severe congestion during peak periods. The problem
is not simply the lack of roads — Nairobi has multiple corridors that
can connect the same origins and destinations.

Traditional navigation finds a currently efficient route, but if a
large number of vehicles are simultaneously given the same route, that
route itself becomes congested.

The project must therefore investigate:

- *What route is likely to be optimal when the vehicle actually reaches
  that part of the network?*
- *How should vehicles be distributed across the network to minimize
  overall congestion and total travel time?*

## 3. Central research question

> Can short-term traffic prediction combined with network-aware routing
> reduce congestion and total travel time across Nairobi's road network?

Experimentally compare:

1. Conventional / current-condition routing
2. Predictive routing
3. Network-aware predictive routing

## 4. System principle: open-source software ≠ open traffic data

The core technology stack is open-source and vendor-neutral.
Proprietary systems (Google Maps, HERE, Waze, TomTom) **may** be used
for research, benchmarking, validation, manual observation, and
comparison — but **must not** be mandatory runtime dependencies.

The platform must be capable of functioning independently using
OpenStreetMap, SUMO, OSRM, PostGIS, GPS observations, authorized CV
observations, manual counts, legal public datasets, and simulated data.

## 5. Philosophy

The system is **not** a Google Maps clone and **not** primarily a route-finding
app. It is a **traffic intelligence system**.

```
OBSERVE → UNDERSTAND → PREDICT → SIMULATE → OPTIMIZE → RECOMMEND → OBSERVE
```

## 6. Geographic scope

MVP focus: Nairobi metropolitan area. Initial experimental corridor:
**Rongai → Nairobi CBD**. Architecture supports expansion to Lang'ata,
Ngong, Karen, Kikuyu, Kiambu, Thika, Mombasa Road, Waiyaki Way,
Westlands, Eastlands, CBD, and beyond.

## 7. Open-source core stack

- **Map data**: OpenStreetMap
- **Geospatial**: OSMnx, GeoPandas, Shapely, GDAL
- **Database**: PostgreSQL + PostGIS
- **Routing**: OSRM (with public-API fallback)
- **Simulation**: SUMO
- **Backend**: Python, Django, Django REST Framework
- **Background**: Celery, Redis
- **Data science**: NumPy, Pandas, scikit-learn
- **Deep learning**: PyTorch (only when justified)
- **Computer vision**: OpenCV, YOLO or similar open detector
- **Frontend**: React, TypeScript, Vite, Tailwind (mobile-first)
- **Map rendering**: MapLibre GL JS
- **Containers**: Docker, Docker Compose
- **VCS**: Git, GitHub

## 8. High-level architecture

```
DATA SOURCES (OSM, GPS, Cameras)
        ↓
   DATA INGESTION
        ↓
  PostgreSQL + PostGIS
        ↓
Traffic State Engine ←→ Historical Dataset
        ↓
 TRAFFIC PREDICTION
        ↓
 PREDICTIVE ROUTING ─→ OSRM + NETWORK OPTIMIZER
        ↓
   DJANGO REST API
        ↓
  REACT + MAPLIBRE
        ↓
 TRAFFIC DASHBOARD (mobile-first)
```

## 9. Data sources

Do not hard-code around a single provider. Create a generic
`TrafficDataSource` interface. Implementations:

1. `SUMOSource`
2. `GPSSource`
3. `CameraSource`
4. `ManualCountSource`
5. `PublicDatasetSource`
6. `GovernmentSource`
7. `ExternalBenchmarkSource` (legal, non-mandatory Google/HERE-style comparisons)

Standardized observation fields:

```
road_id, timestamp, latitude, longitude,
speed, vehicle_count, density, travel_time,
source, confidence
```

## 10–11. Road network & segments

Use OpenStreetMap via OSMnx. Extract roads, geometry, names,
classifications, one-way restrictions, lanes, speed limits,
intersections, connectivity, and turn restrictions where available.
Store in PostGIS.

Distinguish: **Road / Road Segment / Intersection / Corridor**.

Each segment carries: `road_id`, geometry, length, road_type, direction,
lanes, speed_limit, free_flow_speed, capacity, and intersection relations.

## 12. Traffic state estimation

Per segment estimate speed (avg/median), vehicle count, density,
travel_time, queue_length, occupancy, congestion level, confidence.
State classes: `FREE_FLOW`, `LIGHT`, `MODERATE`, `HEAVY`, `SEVERE`. Congestion ratio:

```
congestion_ratio = current_speed / free_flow_speed
```

## 13–15. Simulation / demand / scenarios

Use SUMO. Import the Nairobi network. Model an origin–destination
demand between defined zones (Rongai, Lang'ata, Karen, Ngong, Kikuyu,
Kiambu, Thika, Westlands, Eastlands, CBD…). Every scenario is
reproducible with a scenario_id, configuration, seed, simulation_time,
routing_strategy, and results.

Named scenarios include: `NORMAL_MORNING`, `HEAVY_MORNING`,
`NORMAL_EVENING`, `HEAVY_EVENING`, `RAIN`, `ACCIDENT`,
`ROAD_CLOSURE`, `EVENT`, `INCREASED_DEMAND`.

## 16. Historical dataset

Time-series per segment: timestamps, day/hour/minute, speed, count,
density, travel_time, queue_length, weather, incident, state.

## 17–18. Prediction

Horizons: 5, 10, 15, 30 minutes. Targets: future speed, travel time,
congestion level, queue length.

Start simple: historical average, moving average, linear regression.
Then evaluate Random Forest, Gradient Boosting, XGBoost, LSTM, GRU,
temporal NNs. Do **not** assume deep learning is superior. Track
MAE, RMSE, MAPE (where appropriate), inference time, training time.

## 19–20. Predictive routing & arrival-time prediction

The routing engine must use predicted state *at the time the vehicle
actually reaches each segment*, not current state at request time.

## 21–22. Network effects & optimization

If many vehicles are redirected onto the same alternative, its future
travel time must be recalculated. Support iterative assignment:

```
Demand → assignment → simulation → new state → prediction → reassignment → converge
```

Optimize total network travel time and delay, subject to capacity,
intersection capacity, availability, and demand. Additional objectives:
queue length, average speed, congestion duration, route fairness,
emissions, reliability.

## 23–25. Strategies, OSRM, and commercial systems

Compare at least three strategies:

- **A** — Shortest/fastest conventional
- **B** — Predictive
- **C** — Network-aware predictive

Use OSRM as candidate route generator. Keep the traffic intelligence
layer separate from OSRM. Commercial systems are for benchmarking only
via legal channels — no scraping, no paid dependencies at runtime.

### OSRM failover

The backend `OSRMClient` tries the local OSRM container first, then falls
back to the public OSRM API (`router.project-osrm.org`) when local OSRM is
unavailable. This means route recommendations work even without a built
OSRM graph. The fallback URL is configurable via `OSRM_FALLBACK_URL`.

## 26–29. CV, GPS, map matching, real-time pipeline

CV pipeline: camera → OpenCV → detection → tracking → counting →
speed estimation → traffic state. Vehicle categories include
car, bus, matatu, truck, motorcycle, bicycle.

GPS probe path: receive → validate → map-match → store → aggregate →
update state.

Real-time flow:

```
GPS/Cameras → ingest → validate → map-match → aggregate → state →
prediction → route eval → recommendation
```

## 30. Database

PostGIS. Core tables: `RoadSegment`, `Intersection`, `Corridor`,
`TrafficObservation`, `TrafficState`, `TrafficPrediction`,
`TrafficSimulation`, `SimulationVehicle`, `TrafficScenario`,
`RouteRequest`, `RouteRecommendation`, `TrafficIncident`,
`WeatherObservation`, `TrafficMetric`, `ModelVersion`,
`PredictionResult`.

## 31. API (DRF)

```
GET  /api/roads/
GET  /api/corridors/
GET  /api/traffic/current/
GET  /api/traffic/history/
GET  /api/traffic/predictions/
POST /api/routes/recommend/
GET  /api/routes/
GET  /api/incidents/
GET  /api/simulation/
POST /api/simulation/run/
GET  /api/metrics/
GET  /api/models/
```

The `/api/metrics/` endpoint is served by `django-prometheus` for
Prometheus scraping.

## 32–35. Frontend

React + TypeScript + MapLibre. The frontend is a **mobile-first**
application with:

- **Full-screen map** as the background (MapLibre GL JS)
- **Floating top bar**: hamburger menu, "Where to?" search bar, profile icon
- **Collapsible bottom sheet**: origin/destination inputs with pin icons,
  swap button, departure time, strategy dropdown, "Recommend Routes" CTA
- **Route selection state**: tappable route cards showing time/distance/risk,
  "Start Drive" button
- **Floating map controls**: current-location button (blue arrow) and
  report button (yellow triangle)
- **Any origin, any destination**: tap the map or type coordinates. The old
  Rongai → CBD preset has been removed.

Sections: Live Traffic, Prediction, Route Recommendation, Simulation,
Network Metrics, Historical Analysis.

Route recommendation UI shows current time, predicted time, and risk
per alternative, plus a clear recommendation.

Simulation UI allows configuring origin, destination, vehicle count,
time period, scenario, and routing strategy, and compares strategies.

## 36–40. Evaluation

Every major claim needs simulation or real-world evidence. Metrics:
average and total travel time, total delay, average speed, max/avg
queue length, congestion duration, congested-segment count, route
reliability. Prediction evaluation at every horizon (MAE, RMSE, MAPE).
Routing evaluation compares current-condition vs predictive on
identical network, demand, seed, weather, and incidents.

Baseline experiment: e.g. 10,000 vehicles across 06:30–10:00 from
Rongai → CBD (and other origins), conventional first, then predictive
with everything else held constant.

**Never fabricate performance numbers.**

## 41–48. Data validation, incidents, weather, signals, KURA, security, reliability, modularity

- Compare SUMO ↔ real observations; compare predictions ↔ observed.
- Incidents (accidents, closures, construction, flooding, stalls, events,
  police control) modify capacity, speed, availability, and demand.
- Weather (rainfall, temperature, visibility, severity) is optional and
  only kept if it improves accuracy.
- Traffic signals: model phases and adaptive control later; **do not**
  attempt physical signal control in v1.
- KURA/government: generic integration interface, never a hard dependency.
- Security: no unnecessary PII; anonymize and aggregate GPS; separate
  identity from trajectories.
- Reliability: graceful degradation across missing/late/bad/duplicate
  data and prediction failure; documented fallbacks.
- Modularity: data sources, state, prediction, routing, optimization,
  simulation, API, and frontend are independently replaceable.

## 49. Development phases

Phases 0–11 as listed in [ROADMAP.md](ROADMAP.md).

## 50–51. MVP & first demonstration

MVP shows the full pipeline end-to-end for Rongai → CBD. The first
demo answers: *what happens if we know congestion is about to develop
on the currently fastest route?*

## 52–54. Long-term vision & research contribution

City-scale traffic intelligence platform integrating GPS, cameras,
sensors, detection, prediction, incidents, a network model, predictive
routing, and (eventually) signal optimization. The research question is
whether a low-cost, open-source stack can produce useful predictive
traffic information for a complex African city.

## 55. Constraints — do not

- fabricate traffic data or performance improvements
- assume all roads behave identically
- assume drivers always follow recommendations
- assume the currently fastest route stays fastest
- assume deep learning is automatically superior
- make Google / HERE APIs mandatory
- build the entire system as a monolith
- over-engineer the MVP with Kubernetes / microservices
- deploy traffic-signal control in v1

## 56. Documentation required

System, data, traffic, simulation, prediction, routing, optimization,
API, DB schema, deployment, experiment methodology, evaluation
results, limitations, privacy, future work.

## 57. Engineering standard

Modular code, typed interfaces, config files, env vars, Docker,
automated tests, reproducible experiments, logging, metrics, DB
migrations, API docs, versioned ML models. Every experiment
reproducible; every reported metric traceable.

## 58. Final objective

Demonstrate that:

- A road network can be represented digitally.
- Traffic can be observed.
- Traffic state can be estimated.
- Future traffic can be predicted.
- Alternatives can be evaluated against future traffic.
- Traffic can be redistributed intelligently.
- The effect can be simulated and measured.
- And eventually, real-world traffic can be influenced by an intelligent,
  predictive traffic-management layer.

---

## Final statement

Build an open, vendor-neutral traffic intelligence platform for
Nairobi that does not merely tell drivers where traffic is. It should
learn how Nairobi's road network behaves, predict where congestion is
likely to occur, understand the consequences of routing decisions, and
recommend or eventually optimize traffic movement before congestion
forms.

```
"Where is the traffic?"
    →  "Where will the traffic be?"
    →  "What happens if we send vehicles there?"
    →  "How should we distribute vehicles across the network?"
    →  "How can we proactively manage the entire road network?"
```