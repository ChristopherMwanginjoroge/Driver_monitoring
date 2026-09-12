# Generated migration for traffic_state models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrafficState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('window_start', models.DateTimeField(db_index=True)),
                ('window_end', models.DateTimeField()),
                ('avg_speed_kmh', models.FloatField(blank=True, null=True)),
                ('median_speed_kmh', models.FloatField(blank=True, null=True)),
                ('vehicle_count', models.IntegerField(blank=True, null=True)),
                ('density_vpk', models.FloatField(blank=True, null=True)),
                ('travel_time_s', models.FloatField(blank=True, null=True)),
                ('queue_length_m', models.FloatField(blank=True, null=True)),
                ('congestion_ratio', models.FloatField(blank=True, help_text='current_speed / free_flow_speed', null=True)),
                ('congestion_level', models.CharField(choices=[('free_flow', 'Free flow'), ('light', 'Light'), ('moderate', 'Moderate'), ('heavy', 'Heavy'), ('severe', 'Severe')], default='free_flow', max_length=16)),
                ('confidence', models.FloatField(default=1.0)),
                ('observation_count', models.PositiveIntegerField(default=0)),
                ('road', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='network.roadsegment')),
            ],
        ),
        migrations.AddIndex(
            model_name='trafficstate',
            index=models.Index(fields=['road', 'window_start'], name='traffic_sta_road_id_window_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='trafficstate',
            unique_together={('road', 'window_start')},
        ),
    ]
