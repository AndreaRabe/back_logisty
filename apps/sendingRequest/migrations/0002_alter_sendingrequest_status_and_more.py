# Generated by Django 5.1.5 on 2025-02-18 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sendingRequest', '0001_initial'),
        ('users', '0009_alter_admin_last_admin_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendingrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.CreateModel(
            name='SendingRequestFleetAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('in_progress', 'in_progress'), ('rejected', 'Rejected'), ('completed', 'Completed')], default='in_progress', max_length=20)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Driver', to='users.driver')),
                ('fleet_manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fleet_assignments', to='users.chieffleet')),
                ('sending_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fleet_assignments', to='sendingRequest.sendingrequest')),
            ],
        ),
    ]
