from django.db import models


# Create your models here.
class Truck(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('maintenance', 'Maintenance'),
        ('on mission', 'On Mission'),
    ]

    license_plate = models.CharField(max_length=10, unique=True)  # immatriculation
    brand = models.CharField(max_length=20)  # marque
    model = models.CharField(max_length=20)
    year = models.PositiveIntegerField()  # annee de fabrication
    color = models.CharField(max_length=10, blank=True, null=True)

    last_maintenance_date = models.DateField(null=True, blank=True)
    insurance_expiry_date = models.DateField(null=True, blank=True)
    max_load_capacity = models.FloatField(help_text="Maximum capacity in tonnes")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    last_service_date = models.DateField(blank=True, null=True)

    current_location = models.CharField(max_length=100, blank=True, null=True)
    mileage = models.PositiveIntegerField(blank=True, null=True)  # kilometrage

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional specifications")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"
