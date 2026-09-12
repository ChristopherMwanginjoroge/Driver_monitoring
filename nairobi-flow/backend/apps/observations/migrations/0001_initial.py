# Generated migration for TrafficObservation model

from django.contrib.gis.db import models as gis_models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrafficObservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('location', gis_models.PointField(blank=True, null=True, srid=4326)),
                ('speed_kmh', models.FloatField(blank=True, null=True)),
                ('vehicle_count', models.IntegerField(blank=True, null=True)),
                ('density_vpk', models.FloatField(blank=True, help_text='Vehicles per kilometre', null=True)),
                ('travel_time_s', models.FloatField(blank=True, null=True)),
                ('source', models.CharField(choices=[('sumo', 'SUMO simulation'), ('gps', 'GPS probe'), ('camera', 'Camera / CV'), ('manual', 'Manual count'), ('public', 'Public dataset'), ('government', 'Government feed'), ('external_benchmark', 'External benchmark')], max_length=32)),
                ('confidence', models.FloatField(default=1.0)),
                ('payload', models.JSONField(blank=True, default=dict)),
                ('matched_segment_id', models.IntegerField(blank=True, db_index=True, help_text='OSM way ID from map matching', null=True)),
                ('match_confidence', models.FloatField(blank=True, help_text='Map matching confidence (0.0-1.0)', null=True)),
                ('raw_lat_lon', models.JSONField(blank=True, default=dict, help_text='Original GPS coordinates')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('road', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='observations', to='network.roadsegment')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='trafficobservation',
            index=models.Index(fields=['road', 'timestamp'], name='observations_road_times_idx'),
        ),
        migrations.AddIndex(
            model_name='trafficobservation',
            index=models.Index(fields=['source', 'timestamp'], name='observations_source_times_idx'),
        ),
        migrations.AddIndex(
            model_name='trafficobservation',
            index=models.Index(fields=['matched_segment_id', 'timestamp'], name='observations_segment_times_idx'),
        ),
    ]
