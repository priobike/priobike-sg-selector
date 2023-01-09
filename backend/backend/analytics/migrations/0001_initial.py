# Generated by Django 4.0.1 on 2022-01-06 07:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('routing', '0002_initial'),
        ('composer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('algorithm_name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='RouteAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration_seconds', models.FloatField()),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='composer.route')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.run')),
            ],
        ),
        migrations.CreateModel(
            name='Hit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.TextField()),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hits', to='analytics.routeanalysis')),
                ('lsa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hits', to='routing.lsa')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.run')),
            ],
        ),
    ]
