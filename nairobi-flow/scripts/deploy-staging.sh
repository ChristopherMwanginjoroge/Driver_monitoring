#!/bin/bash
set -e

echo "[$(date)] Starting staging deployment..."

# Pull latest
echo "[$(date)] Pulling latest code..."
git pull origin main || echo "Warning: git pull failed - proceeding with current code"

# Load env
echo "[$(date)] Loading environment..."
if [ -f .env.staging ]; then
  cp .env.staging .env
  echo "✓ Loaded .env.staging"
else
  echo "Warning: .env.staging not found - using existing .env"
fi

# Stop existing containers
echo "[$(date)] Stopping containers..."
docker compose down 2>/dev/null || echo "No containers running"

# Build images
echo "[$(date)] Building images..."
docker compose build backend celery frontend --no-cache

# Start services
echo "[$(date)] Starting services..."
docker compose up -d

# Wait for services to be ready
echo "[$(date)] Waiting for services to become ready..."
sleep 40

# Apply migrations
echo "[$(date)] Applying migrations..."
docker compose exec -T backend python manage.py migrate --noinput

# Collect static files
echo "[$(date)] Collecting static files..."
docker compose exec -T backend python manage.py collectstatic --noinput 2>/dev/null || echo "Warning: Static collection had issues"

# Run tests
echo "[$(date)] Running tests..."
if docker compose exec -T backend pytest backend/tests/ -v --tb=short -x; then
  echo "✓ All tests passed"
else
  echo "⚠ Tests failed - proceeding with deployment (check logs)"
fi

# Health checks
echo "[$(date)] Running health checks..."
HEALTH_CHECKS_PASSED=true

for endpoint in \
  "http://localhost:8000/api/health/" \
  "http://localhost:9090/-/ready" \
  "http://localhost:3000/api/health" \
  "http://localhost:3100/ready"
do
  if curl -sf "$endpoint" > /dev/null 2>&1; then
    echo "✓ $endpoint healthy"
  else
    echo "✗ $endpoint failed"
    HEALTH_CHECKS_PASSED=false
  fi
done

if [ "$HEALTH_CHECKS_PASSED" = true ]; then
  echo "[$(date)] ✅ Staging deployment successful!"
  exit 0
else
  echo "[$(date)] ⚠ Staging deployment completed with health check failures"
  echo "[$(date)] Review logs with: docker compose logs -f"
  exit 1
fi
