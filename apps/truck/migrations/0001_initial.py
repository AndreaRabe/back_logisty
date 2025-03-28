# Generated by Django 5.1.5 on 2025-03-03 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_plate', models.CharField(max_length=10, unique=True)),
                ('brand', models.CharField(max_length=20)),
                ('model', models.CharField(max_length=20)),
                ('year', models.PositiveIntegerField(max_length=4)),
                ('color', models.CharField(blank=True, max_length=10, null=True)),
                ('last_maintenance_date', models.DateField(blank=True, null=True)),
                ('insurance_expiry_date', models.DateField(blank=True, null=True)),
                ('max_load_capacity', models.FloatField(help_text='Capacité maximale en tonnes')),
                ('status', models.CharField(choices=[('available', 'Available'), ('maintenance', 'Maintenance'), ('on mission', 'On Mission')], default='available', max_length=20)),
                ('last_service_date', models.DateField(blank=True, null=True)),
                ('current_location', models.CharField(blank=True, max_length=100, null=True)),
                ('mileage', models.PositiveIntegerField(blank=True, max_length=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, help_text='Specification en plus', null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
