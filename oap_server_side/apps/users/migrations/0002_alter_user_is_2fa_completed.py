# Generated by Django 5.0.6 on 2024-07-25 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_2fa_completed',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]