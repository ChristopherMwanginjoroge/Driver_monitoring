.PHONY: help build up down logs shell migrate makemigrations test \
        extract-osm load-network build-osrm up-osrm frontend-install

help:
	@echo "Common targets:"
	@echo "  build              Build all Docker images"
	@echo "  up                 Start core services (postgis, redis, backend, celery, frontend)"
	@echo "  down               Stop all services"
	@echo "  logs               Tail logs for all services"
	@echo "  shell              Open a Django shell inside the backend"
	@echo "  migrate            Run Django migrations"
	@echo "  makemigrations     Create new Django migrations"
	@echo "  test               Run backend tests"
	@echo "  extract-osm        Fetch Rongai-corridor OSM road network via OSMnx"
	@echo "  load-network       Load the extracted network into PostGIS"
	@echo "  build-osrm         Download+preprocess the OSRM graph (needs Docker)"
	@echo "  up-osrm            Start the OSRM service (needs build-osrm first)"
	@echo "  frontend-install   Install frontend dependencies"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

shell:
	docker compose exec backend python manage.py shell

migrate:
	docker compose exec backend python manage.py migrate

makemigrations:
	docker compose exec backend python manage.py makemigrations

test:
	docker compose exec backend pytest

# scripts/ is bind-mounted to /scripts on the backend container (see compose).
# /data is bind-mounted to ./data.
extract-osm:
	docker compose exec backend python /scripts/extract_osm.py \
	    --scope rongai --data-dir /data/osm

load-network:
	docker compose exec backend python manage.py load_network \
	    --graphml /data/osm/rongai_drive.graphml --wipe

build-osrm:
	bash scripts/build_osrm.sh

up-osrm:
	docker compose --profile routing up -d osrm

frontend-install:
	docker compose exec frontend npm install
