# Generated by Django 5.0.6 on 2024-11-05 21:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("media", "0002_initial"),
        ("video", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transcript",
            name="transcriptionLanguage",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transcripts",
                to="media.originallanguage",
            ),
        ),
    ]
