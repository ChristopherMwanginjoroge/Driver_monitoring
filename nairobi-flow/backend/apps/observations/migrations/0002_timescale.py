# TimescaleDB migration for hypertable optimization

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;",
            reverse_sql="DROP EXTENSION IF EXISTS timescaledb CASCADE;",
        ),
        migrations.RunSQL(
            sql="""
            SELECT create_hypertable(
                'observations_trafficobservation',
                'timestamp',
                if_not_exists => TRUE
            );
            """,
            reverse_sql="SELECT detach_hypertable('observations_trafficobservation');",
        ),
    ]
