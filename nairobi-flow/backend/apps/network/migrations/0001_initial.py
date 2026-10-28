# Generated migration for network models

from django.contrib.gis.db import models as gis_models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Intersection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('osm_node_id', models.BigIntegerField(blank=True, null=True, unique=True)),
                ('geometry', gis_models.PointField(srid=4326)),
                ('signalized', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='RoadSegment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('osm_way_id', models.BigIntegerField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('road_type', models.CharField(choices=[('motorway', 'Motorway'), ('trunk', 'Trunk'), ('primary', 'Primary'), ('secondary', 'Secondary'), ('tertiary', 'Tertiary'), ('residential', 'Residential'), ('service', 'Service'), ('unclassified', 'Unclassified'), ('other', 'Other')], default='other', max_length=32)),
                ('geometry', gis_models.LineStringField(srid=4326)),
                ('length_m', models.FloatField(help_text='Segment length in metres')),
                ('lanes', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('one_way', models.BooleanField(default=False)),
                ('speed_limit_kmh', models.FloatField(blank=True, null=True)),
                ('free_flow_speed_kmh', models.FloatField(blank=True, null=True)),
                ('capacity_vph', models.FloatField(blank=True, help_text='Estimated capacity in vehicles/hour', null=True)),
                ('end_node', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='incoming_segments', to='network.intersection')),
                ('start_node', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='outgoing_segments', to='network.intersection')),
            ],
        ),
        migrations.CreateModel(
            name='Corridor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CorridorSegment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('corridor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.corridor')),
                ('segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.roadsegment')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('corridor', 'order')},
            },
        ),
        migrations.AddField(
            model_name='corridor',
            name='segments',
            field=models.ManyToManyField(related_name='corridors', through='network.CorridorSegment', to='network.RoadSegment'),
        ),
        migrations.AddIndex(
            model_name='roadsegment',
            index=models.Index(fields=['osm_way_id'], name='network_roadsegment_osm_way_id_idx'),
        ),
        migrations.AddIndex(
            model_name='roadsegment',
            index=models.Index(fields=['road_type'], name='network_roadsegment_road_type_idx'),
        ),
        migrations.AddIndex(
            model_name='intersection',
            index=models.Index(fields=['osm_node_id'], name='network_intersection_osm_node_id_idx'),
        ),
    ]
