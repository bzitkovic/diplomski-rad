# Generated by Django 4.0.5 on 2022-07-10 21:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cycling_networking', '0007_user_bio_user_name_alter_user_email_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rides',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('start_latitude', models.FloatField()),
                ('start_longitude', models.FloatField()),
                ('end_latitude', models.FloatField()),
                ('end_longitude', models.FloatField()),
                ('description', models.TextField(null=True)),
                ('cyclist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
