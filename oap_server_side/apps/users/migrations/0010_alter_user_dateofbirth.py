# Generated by Django 5.0.6 on 2024-06-24 09:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_user_dateofbirth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dateOfBirth',
            field=models.DateField(default=datetime.datetime(2024, 6, 24, 9, 56, 20, 641415, tzinfo=datetime.timezone.utc)),
        ),
    ]