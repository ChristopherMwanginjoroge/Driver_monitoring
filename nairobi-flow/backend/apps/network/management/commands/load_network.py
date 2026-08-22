"""Management command: load a NetworkX graph produced by OSMnx into PostGIS.

Usage:
    python manage.py load_network --graphml /data/osm/nairobi_drive.graphml

The extraction step (scripts/extract_osm.py) writes GraphML files to the
mounted /data volume. This command imports them into the RoadSegment /
Intersection tables.
"""
from __future__ import annotations

from pathlib import Path

from django.contrib.gis.geos import LineString, Point
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.network.models import Intersection, RoadSegment, RoadType

try:
    import networkx as nx
    import osmnx as ox
except ImportError as exc:  # pragma: no cover
    raise CommandError(
        "osmnx and networkx are required. Install backend requirements."
    ) from exc


ROAD_TYPE_MAP = {choice.value: choice.value for choice in RoadType}


def _classify(highway_tag: str | list[str] | None) -> str:
    if isinstance(highway_tag, list):
        highway_tag = highway_tag[0] if highway_tag else None
    if not highway_tag:
        return RoadType.OTHER
    return ROAD_TYPE_MAP.get(highway_tag, RoadType.OTHER)


def _first_float(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, list):
        value = value[0] if value else None
    try:
        return float(str(value).split()[0])
    except (TypeError, ValueError):
        return None


class Command(BaseCommand):
    help = "Load an OSMnx-produced GraphML file into PostGIS."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--graphml", required=True, help="Path to .graphml")
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Delete existing network rows before loading",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        path = Path(options["graphml"])
        if not path.exists():
            raise CommandError(f"GraphML not found: {path}")

        self.stdout.write(f"Reading {path}...")
        graph = ox.load_graphml(path)
        self.stdout.write(
            f"  nodes={graph.number_of_nodes()} edges={graph.number_of_edges()}"
        )

        if options["wipe"]:
            self.stdout.write("Wiping existing RoadSegment / Intersection rows...")
            RoadSegment.objects.all().delete()
            Intersection.objects.all().delete()

        node_lookup: dict[int, Intersection] = {}
        for osm_id, data in graph.nodes(data=True):
            point = Point(float(data["x"]), float(data["y"]), srid=4326)
            node, _ = Intersection.objects.update_or_create(
                osm_node_id=int(osm_id),
                defaults={"geometry": point},
            )
            node_lookup[int(osm_id)] = node

        segments_created = 0
        for u, v, key, data in graph.edges(keys=True, data=True):
            geom = data.get("geometry")
            if geom is not None:
                coords = list(geom.coords)
            else:
                u_data, v_data = graph.nodes[u], graph.nodes[v]
                coords = [(u_data["x"], u_data["y"]), (v_data["x"], v_data["y"])]
            line = LineString(coords, srid=4326)

            RoadSegment.objects.create(
                osm_way_id=int(data.get("osmid", key) if isinstance(data.get("osmid"), int) else 0) or None,
                name=str(data.get("name", "") or "")[:255],
                road_type=_classify(data.get("highway")),
                geometry=line,
                length_m=float(data.get("length", 0.0) or 0.0),
                lanes=int(_first_float(data.get("lanes")) or 0) or None,
                one_way=bool(data.get("oneway", False)),
                speed_limit_kmh=_first_float(data.get("maxspeed")),
                start_node=node_lookup.get(int(u)),
                end_node=node_lookup.get(int(v)),
            )
            segments_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Loaded {segments_created} segments and {len(node_lookup)} intersections."
        ))
