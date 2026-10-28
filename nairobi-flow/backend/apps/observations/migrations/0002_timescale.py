from django.db import migrations

_CREATE_HYPERTABLE = """\
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb'
  ) THEN
    CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
    PERFORM create_hypertable(
      'observations_trafficobservation',
      'timestamp',
      if_not_exists => TRUE
    );
  END IF;
END
$$;
"""

_DETACH_HYPERTABLE = """\
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'
  ) THEN
    PERFORM detach_hypertable('observations_trafficobservation');
    DROP EXTENSION IF EXISTS timescaledb CASCADE;
  END IF;
END
$$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("observations", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=_CREATE_HYPERTABLE,
            reverse_sql=_DETACH_HYPERTABLE,
        ),
    ]