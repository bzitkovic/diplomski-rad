# Generated by Django 4.0.5 on 2022-07-16 12:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cycling_networking', '0013_event_end_latitude_event_end_longitude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='cyclist',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]