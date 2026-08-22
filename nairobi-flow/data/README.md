# Local data (git-ignored)

Nothing sensitive or heavy is committed here. Contents of subdirectories
are ignored by `.gitignore`, but the folders themselves are kept for
convenience.

```
data/
  osm/          Raw OSM extracts + OSMnx GraphML files
  raw/          Raw ingested observations (SUMO FCD, GPS dumps, CV counts)
  processed/    Cleaned/aggregated derivatives ready for training
  sumo/         Simulation outputs (FCD, edge-data, tripinfo)
```

## Privacy

GPS observations must be anonymized before landing in `raw/`.
Never commit files that link a `client_id` to a full trajectory.
Aggregate before publishing anything from `processed/`.
