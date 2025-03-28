# Generated by Django 5.1.5 on 2025-03-06 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_admin_last_admin_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('suspended', 'Suspended'), ('pending', 'Pending'), ('banned', 'Banned')], default='pending', max_length=20),
        ),
    ]
