# Generated migration for simulation models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('routing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrafficScenario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('normal_morning', 'Normal morning'), ('heavy_morning', 'Heavy morning'), ('normal_evening', 'Normal evening'), ('heavy_evening', 'Heavy evening'), ('rain', 'Rain'), ('accident', 'Accident'), ('road_closure', 'Road closure'), ('event', 'Event'), ('increased_demand', 'Increased demand')], max_length=64)),
                ('description', models.TextField(blank=True)),
                ('config', models.JSONField(blank=True, default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='TrafficSimulation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('routing_strategy', models.CharField(choices=[('conventional', 'Conventional (current-condition)'), ('predictive', 'Predictive'), ('network_aware', 'Network-aware predictive')], default='conventional', max_length=32)),
                ('random_seed', models.IntegerField()),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('duration_s', models.FloatField(blank=True, null=True)),
                ('metrics', models.JSONField(blank=True, default=dict)),
                ('artifact_path', models.CharField(blank=True, max_length=500)),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='runs', to='simulation.trafficscenario')),
            ],
        ),
        migrations.CreateModel(
            name='SimulationVehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_id', models.CharField(max_length=64)),
                ('origin_zone', models.CharField(max_length=64)),
                ('destination_zone', models.CharField(max_length=64)),
                ('departure_s', models.FloatField()),
                ('arrival_s', models.FloatField(blank=True, null=True)),
                ('travel_time_s', models.FloatField(blank=True, null=True)),
                ('distance_m', models.FloatField(blank=True, null=True)),
                ('simulation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='simulation.trafficsimulation')),
            ],
        ),
        migrations.AddIndex(
            model_name='trafficsimulation',
            index=models.Index(fields=['scenario', 'routing_strategy'], name='simulation_traffic_sim_scenario_strategy_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='simulationvehicle',
            unique_together={('simulation', 'vehicle_id')},
        ),
    ]
