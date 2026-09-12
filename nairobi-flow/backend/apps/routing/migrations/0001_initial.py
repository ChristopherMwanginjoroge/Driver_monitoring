# Generated migration for routing models

from django.contrib.gis.db import models as gis_models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RouteRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origin', gis_models.PointField(srid=4326)),
                ('destination', gis_models.PointField(srid=4326)),
                ('departure_time', models.DateTimeField()),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('strategy', models.CharField(choices=[('conventional', 'Conventional (current-condition)'), ('predictive', 'Predictive'), ('network_aware', 'Network-aware predictive')], default='conventional', max_length=32)),
                ('client_id', models.CharField(blank=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='RouteRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.PositiveSmallIntegerField()),
                ('geometry', gis_models.LineStringField(srid=4326)),
                ('current_travel_time_s', models.FloatField(blank=True, null=True)),
                ('predicted_travel_time_s', models.FloatField(blank=True, null=True)),
                ('risk_level', models.CharField(blank=True, max_length=16)),
                ('strategy', models.CharField(choices=[('conventional', 'Conventional (current-condition)'), ('predictive', 'Predictive'), ('network_aware', 'Network-aware predictive')], default='conventional', max_length=32)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='routing.routerequest')),
            ],
            options={
                'ordering': ['request', 'rank'],
            },
        ),
    ]
