# Generated by Django 4.1.3 on 2022-11-03 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routing', '0005_remove_lsa_md5_delete_lsacell'),
    ]

    operations = [
        migrations.AddField(
            model_name='lsametadata',
            name='datastream_cycle_second_id',
            field=models.CharField(max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='lsametadata',
            name='datastream_detector_car_id',
            field=models.CharField(max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='lsametadata',
            name='datastream_detector_cyclists_id',
            field=models.CharField(max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='lsametadata',
            name='datastream_primary_signal_id',
            field=models.CharField(max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='lsametadata',
            name='datastream_signal_program_id',
            field=models.CharField(max_length=25, null=True),
        ),
    ]
