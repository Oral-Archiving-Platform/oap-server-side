# Generated by Django 5.0.6 on 2024-08-17 21:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0002_alter_channelmembership_unique_together'),
        ('playlist', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='channel.channel'),
        ),
    ]