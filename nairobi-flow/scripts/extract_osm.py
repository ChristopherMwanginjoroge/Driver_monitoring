"""Extract the Nairobi road network from OpenStreetMap using OSMnx.

Writes a GraphML file to `data/osm/`, which the Django management
command `load_network` then imports into PostGIS.

Usage:
    python scripts/extract_osm.py --scope rongai
    python scripts/extract_osm.py --scope nairobi
    python scripts/extract_osm.py --place "Rongai, Kajiado, Kenya" --out data/osm/rongai.graphml
"""
from __future__ import annotations

import argparse
from pathlib import Path

import osmnx as ox


SCOPES = {
    "rongai": {
        # Bounding box around the Rongai → Nairobi CBD corridor.
        # (north, south, east, west) roughly captures Ngong Road, Lang'ata Road,
        # Southern Bypass, and the CBD.
        "bbox": (-1.230, -1.460, 37.010, 36.660),
        "description": "Rongai → Nairobi CBD MVP corridor",
    },
    "nairobi": {
        "place": "Nairobi, Kenya",
        "description": "Full Nairobi metropolitan area",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=SCOPES.keys(), default="rongai")
    parser.add_argument(
        "--place",
        help="Override: OSMnx place query (skips built-in scope)",
    )
    parser.add_argument("--network-type", default="drive")
    parser.add_argument(
        "--out",
        default=None,
        help="Output GraphML path (defaults to data/osm/<scope>.graphml)",
    )
    parser.add_argument(
        "--data-dir",
        default="data/osm",
        help="Data directory root (relative to CWD)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.data_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else out_dir / f"{args.scope}_{args.network_type}.graphml"

    ox.settings.log_console = True

    if args.place:
        graph = ox.graph_from_place(args.place, network_type=args.network_type)
    elif "bbox" in SCOPES[args.scope]:
        north, south, east, west = SCOPES[args.scope]["bbox"]
        graph = ox.graph_from_bbox(
            bbox=(north, south, east, west),
            network_type=args.network_type,
        )
    else:
        graph = ox.graph_from_place(SCOPES[args.scope]["place"], network_type=args.network_type)

    print(f"nodes={graph.number_of_nodes()} edges={graph.number_of_edges()}")
    ox.save_graphml(graph, filepath=out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
