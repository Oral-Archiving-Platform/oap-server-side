# Generated by Django 5.0.6 on 2024-09-23 10:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_remove_video_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name', models.CharField(max_length=100)),
                ('city_image', models.ImageField(upload_to='cities/')),
            ],
        ),
        migrations.RemoveField(
            model_name='video',
            name='location',
        ),
        migrations.AddField(
            model_name='video',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videos', to='video.city'),
        ),
        migrations.CreateModel(
            name='Monument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monument_name', models.CharField(max_length=100)),
                ('monument_image', models.ImageField(upload_to='monuments/')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monuments', to='video.city')),
            ],
        ),
        migrations.AddField(
            model_name='video',
            name='monument',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videos', to='video.monument'),
        ),
    ]