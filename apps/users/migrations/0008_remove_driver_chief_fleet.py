# Generated by Django 5.1.5 on 2025-02-13 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_driver_chief_fleet_alter_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='driver',
            name='chief_fleet',
        ),
    ]
