# Generated migration for prediction models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('version', models.CharField(max_length=50)),
                ('algorithm', models.CharField(max_length=100)),
                ('trained_at', models.DateTimeField(auto_now_add=True)),
                ('params', models.JSONField(blank=True, default=dict)),
                ('metrics', models.JSONField(blank=True, default=dict)),
                ('artifact_path', models.CharField(blank=True, max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='TrafficPrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('made_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('target_time', models.DateTimeField(db_index=True)),
                ('horizon_minutes', models.PositiveSmallIntegerField()),
                ('predicted_speed_kmh', models.FloatField(blank=True, null=True)),
                ('predicted_travel_time_s', models.FloatField(blank=True, null=True)),
                ('predicted_congestion_ratio', models.FloatField(blank=True, null=True)),
                ('confidence', models.FloatField(default=1.0)),
                ('model_version', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='predictions', to='prediction.modelversion')),
                ('road', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predictions', to='network.roadsegment')),
            ],
        ),
        migrations.CreateModel(
            name='PredictionResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observed_speed_kmh', models.FloatField(blank=True, null=True)),
                ('observed_travel_time_s', models.FloatField(blank=True, null=True)),
                ('absolute_error', models.FloatField(blank=True, null=True)),
                ('squared_error', models.FloatField(blank=True, null=True)),
                ('percent_error', models.FloatField(blank=True, null=True)),
                ('prediction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='prediction.trafficprediction')),
            ],
        ),
        migrations.AddIndex(
            model_name='trafficprediction',
            index=models.Index(fields=['road', 'target_time'], name='prediction_trafficpred_road_target_idx'),
        ),
        migrations.AddIndex(
            model_name='trafficprediction',
            index=models.Index(fields=['model_version', 'made_at'], name='prediction_trafficpred_model_made_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='modelversion',
            unique_together={('name', 'version')},
        ),
    ]
