# Generated by Django 4.0.3 on 2022-03-16 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routing', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lsa',
            name='md5',
            field=models.CharField(default='', max_length=32),
        ),
    ]
