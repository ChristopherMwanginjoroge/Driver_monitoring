#!/usr/bin/env bash
# Build the OSRM graph used by the routing engine.
#
# Downloads a Kenya OSM PBF, optionally clips it to a bounding box for
# faster iteration, and runs osrm-extract / osrm-partition / osrm-customize
# using the official osrm/osrm-backend image (MLD algorithm — supports
# fast weight updates for predictive routing).
#
# Environment variables:
#   DATA_DIR    Output directory (default: services/osrm/data)
#   PBF_URL     Source PBF (default: Geofabrik Kenya latest)
#   BBOX        west,south,east,north (default: Rongai corridor)
#   SKIP_CLIP=1 Skip bbox clipping and use the full Kenya PBF
#
# Requires: bash, curl, docker.
set -euo pipefail

DATA_DIR="${DATA_DIR:-services/osrm/data}"
PBF_URL="${PBF_URL:-https://download.geofabrik.de/africa/kenya-latest.osm.pbf}"
BBOX="${BBOX:-36.660,-1.460,37.010,-1.230}"
OSRM_IMAGE="${OSRM_IMAGE:-osrm/osrm-backend:latest}"
OSMIUM_IMAGE="${OSMIUM_IMAGE:-stefda/osmium-tool}"

mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

PBF_NAME="$(basename "$PBF_URL")"

if [ ! -f "$PBF_NAME" ]; then
    echo "→ downloading $PBF_URL"
    curl -L --fail --retry 3 -o "$PBF_NAME" "$PBF_URL"
fi

if [ "${SKIP_CLIP:-0}" = "1" ]; then
    SRC_PBF="$PBF_NAME"
else
    SRC_PBF="nairobi.osm.pbf"
    if [ ! -f "$SRC_PBF" ]; then
        echo "→ clipping to bbox $BBOX"
        if command -v osmium >/dev/null 2>&1; then
            osmium extract --bbox "$BBOX" --overwrite \
                --output "$SRC_PBF" "$PBF_NAME"
        else
            docker run --rm -v "$PWD:/data" "$OSMIUM_IMAGE" \
                osmium extract --bbox "$BBOX" --overwrite \
                --output "/data/$SRC_PBF" "/data/$PBF_NAME"
        fi
    fi
fi

BASE="${SRC_PBF%.osm.pbf}"

echo "→ osrm-extract"
docker run --rm -v "$PWD:/data" "$OSRM_IMAGE" \
    osrm-extract -p /opt/car.lua "/data/$SRC_PBF"

echo "→ osrm-partition"
docker run --rm -v "$PWD:/data" "$OSRM_IMAGE" \
    osrm-partition "/data/${BASE}.osrm"

echo "→ osrm-customize"
docker run --rm -v "$PWD:/data" "$OSRM_IMAGE" \
    osrm-customize "/data/${BASE}.osrm"

# Compose expects /data/nairobi.osrm. If we clipped to nairobi.osm.pbf
# that's already the case; otherwise the base name matches the PBF.
if [ "$BASE" != "nairobi" ]; then
    echo "→ note: compose expects /data/nairobi.osrm; current base is $BASE"
    echo "        edit docker-compose.yml OSRM command to point to ${BASE}.osrm"
fi

echo "✓ OSRM graph ready in $DATA_DIR"
