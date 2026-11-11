# Grafana Dashboard Queries

## Key Performance Indicators

### 1. Data Pipeline Lag
Measures the freshness of traffic observations in the database.

**SQL Query:**
```sql
SELECT max(timestamp) FROM observations_trafficobservation
```

**Description:**
Shows the timestamp of the most recent observation. Use this to monitor data ingestion latency. If the max timestamp is significantly older than current time, the data pipeline is lagging.

---

### 2. Map Match Success Rate
Measures the percentage of traffic observations successfully matched to the road network.

**SQL Query:**
```sql
SELECT count(*) FILTER (WHERE match_confidence > 0.8) / count(*) 
FROM observations_trafficobservation 
WHERE timestamp > now() - interval '1 hour'
```

**Description:**
Calculates the proportion of observations in the last hour with match_confidence > 0.8 (high confidence). A high rate (>95%) indicates good map matching performance. Lower rates suggest issues with GPS quality or network data.

---

### 3. API Latency (95th Percentile)
Measures request processing time at the 95th percentile.

**Prometheus Query:**
```promql
histogram_quantile(0.95, rate(django_http_request_duration_seconds_bucket[5m]))
```

**Description:**
Returns the 95th percentile of request duration over a 5-minute window. This captures typical worst-case performance for API responses. Look for increases to identify performance regressions.

---

### 4. Database Connections
Shows active database connections.

**Prometheus Query:**
```promql
pg_stat_activity_count
```

**Description:**
Exported by postgres_exporter from the pg_stat_activity view. Monitor spikes which may indicate connection leaks or high query load.

---

## Additional Useful Queries

### Request Rate by Endpoint
```promql
rate(django_http_requests_total[5m])
```

### Error Rate (4xx and 5xx)
```promql
rate(django_http_requests_total{status=~"[45].."}[5m])
```

### Celery Task Execution Time
```promql
histogram_quantile(0.95, rate(celery_task_runtime_seconds_bucket[5m]))
```

### PostgreSQL Query Performance
```sql
SELECT mean_exec_time, query FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10
```

---

## Dashboard Setup Tips

1. **Time Range**: Default to 1 hour for real-time monitoring, 24 hours for trend analysis
2. **Refresh Rate**: Set to 30 seconds for live dashboards
3. **Alerts**: Set up alerts when:
   - Data lag exceeds 5 minutes
   - Map match success rate < 90%
   - API p95 latency > 500ms
   - Database connections > 80% of max_connections
4. **Loki Log Queries**: Filter logs by service and environment:
   ```
   {service="backend", environment="production"}
   ```

## Prometheus Configuration

The Django backend exposes metrics at `/api/metrics/` (via `django-prometheus`).
Prometheus is configured to scrape this endpoint in `monitoring/prometheus.yml`.
The path was changed from `/metrics` to `/api/metrics/` to align with DRF
routing conventions.