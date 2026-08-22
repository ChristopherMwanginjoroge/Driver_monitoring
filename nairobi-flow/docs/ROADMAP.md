# Roadmap

Phased plan mirroring the project brief. Each phase produces something
demonstrable and reproducible.

| Phase | Name                        | Outcome                                                   |
|-------|-----------------------------|-----------------------------------------------------------|
| 0     | Research                    | Notes on Nairobi patterns and comparable ITS systems       |
| 1     | Road network                | OSM → OSMnx → PostGIS graph for Nairobi (Rongai corridor)  |
| 2     | Routing                     | OSRM deployed, candidate routes API                        |
| 3     | Traffic simulation          | SUMO network + realistic demand for peak scenarios         |
| 4     | Data platform               | Observation, state, and prediction pipelines               |
| 5     | Prediction                  | Baselines then ML at 5/10/15/30 min horizons               |
| 6     | Predictive routing          | Arrival-time-aware route scoring                           |
| 7     | Network optimization        | Iterative traffic assignment; total-network metrics        |
| 8     | Dashboard                   | MapLibre/React UI with live + predicted layers             |
| 9     | Real data                   | GPS probes, authorized cameras, manual counts, open data   |
| 10    | Calibration                 | Simulation vs. observed vs. commercial systems             |
| 11    | Pilot                       | Small consenting user group; measured outcomes             |

## MVP definition

The MVP succeeds when this pipeline runs end-to-end for the
**Rongai → Nairobi CBD** corridor:

```
OSM → OSMnx → PostGIS → SUMO → traffic state → prediction →
OSRM candidates → predictive selection → SUMO re-simulation →
comparison → MapLibre dashboard
```

## First demonstration

Answer: *what happens if we know congestion is about to develop on the
currently fastest route?*

Show:

- Route A currently fastest.
- Prediction: Route A becomes heavily congested in 10–15 minutes.
- System recommends Route B.
- Re-simulation confirms measured improvement.

Only report numbers produced by the experiment.
