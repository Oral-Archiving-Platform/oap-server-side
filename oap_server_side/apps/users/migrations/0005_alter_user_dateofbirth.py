# Generated by Django 5.0.6 on 2024-06-11 14:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_dateofbirth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dateOfBirth',
            field=models.DateField(default=datetime.datetime(2024, 6, 11, 14, 14, 58, 633318, tzinfo=datetime.timezone.utc)),
        ),
    ]