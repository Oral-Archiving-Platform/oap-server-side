# Generated by Django 5.0.6 on 2024-11-07 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("media", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="media",
            name="acknowledgement",
            field=models.TextField(),
        ),
    ]
