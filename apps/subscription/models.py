from django.db import models

from apps.users.models import Member


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)  # Nom du plan (ex. "Basic", "Pro", "Enterprise")
    description = models.TextField()  # Description du plan
    price = models.IntegerField()  # Prix mensuel/annuel
    duration_month = models.PositiveIntegerField()  # Durée du plan en mois (ex: 1 mois ou bien 12 mois)
    features = models.JSONField(
        default=dict)  # Fonctionnalités incluses (ex. {"priority_support": True, "advanced_reporting": False})
    is_active = models.BooleanField(default=True)  # Plan actif ou désactivé

    def __str__(self):
        return f"{self.name} ({self.price} Ar) and duration ({self.duration_month})"


class Subscription(models.Model):
    client = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='subscriptions')
    sub_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE,
                                 related_name='subscriptions')  # Plan choisi
    start_date = models.DateField(auto_now_add=True)  # Date de début
    end_date = models.DateField(blank=True, null=True)  # Date de fin
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        default='active'
    )

    def __str__(self):
        return f"{self.client} - {self.sub_plan} ({self.status})"
