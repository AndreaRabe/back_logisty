# Generated by Django 5.1.5 on 2025-02-12 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_chieffleet_driverchiefrequest_chieffleet_drivers'),
    ]

    operations = [
        migrations.AddField(
            model_name='chieffleet',
            name='company_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
