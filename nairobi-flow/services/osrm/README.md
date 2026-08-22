# OSRM

OSRM (Open Source Routing Machine) provides candidate routes for the
traffic-intelligence layer. This directory holds prebuild inputs for the
`osrm/osrm-backend` container defined (commented) in `docker-compose.yml`.

## Preparing the graph

1. Download a Kenya extract from Geofabrik (or clip yourself):

   ```sh
   mkdir -p services/osrm/data
   curl -L -o services/osrm/data/kenya-latest.osm.pbf \
     https://download.geofabrik.de/africa/kenya-latest.osm.pbf
   ```

2. Run the OSRM preprocessing pipeline (MLD profile — good for
   frequently changing weights):

   ```sh
   cd services/osrm/data
   docker run --rm -v "$PWD:/data" osrm/osrm-backend \
     osrm-extract -p /opt/car.lua /data/kenya-latest.osm.pbf
   docker run --rm -v "$PWD:/data" osrm/osrm-backend \
     osrm-partition /data/kenya-latest.osrm
   docker run --rm -v "$PWD:/data" osrm/osrm-backend \
     osrm-customize /data/kenya-latest.osrm
   mv kenya-latest.osrm* .
   ```

3. Uncomment the `osrm` service in `docker-compose.yml` and adjust the
   `.osrm` filename to match your build (e.g. `nairobi.osrm`).

## Why MLD

MLD supports quick weight updates, which the predictive-routing layer
needs when segment travel times are re-scored from ML predictions.
CH is faster to query but expensive to rebuild.

## Notes

- OSRM is a candidate-route generator only. Traffic intelligence
  (prediction, network effects) lives in Django, not in OSRM.
- Do not rely on public OSRM demo servers; run locally.
