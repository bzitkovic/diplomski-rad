# Generated by Django 4.0.5 on 2022-07-16 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cycling_networking', '0011_user_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('date', models.DateTimeField()),
                ('entry_fee', models.IntegerField()),
                ('url', models.CharField(max_length=255, null=True)),
            ],
        ),
    ]