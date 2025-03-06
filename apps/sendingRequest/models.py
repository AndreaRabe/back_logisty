from django.db import models

from apps.truck.models import Truck
from apps.users.models import Member, ChiefFleet, Driver


class SendingRequest(models.Model):
    # Types de cargaison (Cargo Types)
    CARGO_TYPE_CHOICES = [
        ('container', 'Container'),
        ('pallets_boxes', 'Pallets and Boxes'),
        ('bulk_fret', 'Bulk Fret (Liquid, Sand, Food Products)'),
        ('vehicle', 'Vehicle'),
        ('animals', 'Animals'),
        ('furniture_tools', 'Furniture or Tools'),
        ('other', 'Other'),
    ]

    # Priorité de la demande (Request Priority)
    PRIORITY_CHOICES = [
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    # Statut de la demande (Request Status)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),  # When payment is done
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Mode de paiement (Payment Method)
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]

    # Informations sur le demandeur (Requester Information)
    client = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='sending_requests')
    recipient_name = models.CharField(max_length=150)
    recipient_email = models.EmailField()
    recipient_phone = models.CharField(max_length=15)

    # Détails du colis (Cargo Details)
    cargo_type = models.CharField(max_length=50, choices=CARGO_TYPE_CHOICES)
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in kg")
    dimensions = models.CharField(max_length=100, help_text="Dimensions in LxWxH format (e.g., 100x50x30 cm)")
    quantity = models.PositiveIntegerField(help_text="Number of items or quantity")

    # Lieu, date et heure de récupération (Pickup Details)
    pickup_location = models.CharField(max_length=100)
    pickup_date_time = models.DateTimeField()

    # Lieu, date et heure de livraison (Delivery Details)
    delivery_location = models.CharField(max_length=100)
    delivery_date_time = models.DateTimeField()

    # Autres spécifications détaillées (Additional Specifications)
    additional_details = models.TextField(blank=True, null=True, help_text="e.g., perishable goods, fragile items")

    # Photos ou documents joints (Attached Files)
    attached_files = models.FileField(upload_to='sending_requests', blank=True, null=True, default=None)

    # Conditions spéciales (Special Conditions)
    special_conditions = models.TextField(blank=True, null=True,
                                          help_text="e.g., refrigeration required, special handling")

    # Priorité de la demande (Request Priority)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    # Prix de base pour le transport
    base_price = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        help_text="Base price for the transport service",
        blank=True,
        null=True
    )

    # Taux de commission (en pourcentage)
    commission_rate = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        help_text="Commission rate as a percentage (e.g., 5.00 for 5%)",
        blank=True,
        null=True
    )

    # Prix total (calculé automatiquement)
    total_price = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        help_text="Total price including commission",
        blank=True,
        null=True
    )

    # Métadonnées de la demande (Request Metadata)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Sending Request #{self.client} - {self.cargo_type} ({self.pickup_location} → {self.delivery_location})"

    class Meta:
        verbose_name = "Sending Request"
        verbose_name_plural = "Sending Requests"


class DeliveryNote(models.Model):
    # Types de cargaison (Cargo Types)
    CARGO_TYPE_CHOICES = [
        ('container', 'Container'),
        ('pallets_boxes', 'Pallets and Boxes'),
        ('bulk_fret', 'Bulk Fret (Liquid, Sand, Food Products)'),
        ('vehicle', 'Vehicle'),
        ('animals', 'Animals'),
        ('furniture_tools', 'Furniture or Tools'),
        ('other', 'Other'),
    ]

    # Priorité de la demande (Request Priority)
    PRIORITY_CHOICES = [
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    # Statut de la demande (Request Status)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),  # When payment is done
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Mode de paiement (Payment Method)
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]

    # Informations sur le demandeur (Requester Information)
    client = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='delivery_note')
    recipient_name = models.CharField(max_length=150)
    recipient_email = models.EmailField()
    recipient_phone = models.CharField(max_length=15)

    # Détails du colis (Cargo Details)
    cargo_type = models.CharField(max_length=50, choices=CARGO_TYPE_CHOICES)
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in kg")
    dimensions = models.CharField(max_length=100, help_text="Dimensions in LxWxH format (e.g., 100x50x30 cm)")
    quantity = models.PositiveIntegerField(help_text="Number of items or quantity")

    # Lieu, date et heure de récupération (Pickup Details)
    pickup_location = models.CharField(max_length=100)
    pickup_date_time = models.DateTimeField()

    # Lieu, date et heure de livraison (Delivery Details)
    delivery_location = models.CharField(max_length=100)
    delivery_date_time = models.DateTimeField()

    # Autres spécifications détaillées (Additional Specifications)
    additional_details = models.TextField(blank=True, null=True, help_text="e.g., perishable goods, fragile items")

    # Photos ou documents joints (Attached Files)
    attached_files = models.FileField(upload_to='sending_requests', blank=True, null=True, default=None)

    # Conditions spéciales (Special Conditions)
    special_conditions = models.TextField(blank=True, null=True,
                                          help_text="e.g., refrigeration required, special handling")

    # Priorité de la demande (Request Priority)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    # Métadonnées de la demande (Request Metadata)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Sending Request #{self.client} - {self.cargo_type} ({self.pickup_location} → {self.delivery_location})"

    class Meta:
        verbose_name = "Sending Request"
        verbose_name_plural = "Sending Requests"


class SendingRequestFleetAssignment(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'in_progress'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('assigned', 'Assigned')
    ]

    sending_request = models.ForeignKey(SendingRequest, on_delete=models.CASCADE, related_name='fleet_assignments')
    fleet_manager = models.ForeignKey(ChiefFleet, on_delete=models.CASCADE, related_name='fleet_assignments')
    delivery_note = models.ForeignKey(DeliveryNote, on_delete=models.CASCADE, related_name='fleet_assignments',
                                      null=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, related_name="Driver", null=True)
    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, related_name="Truck", null=True)

    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')

    def __str__(self):
        return f"Sending Request {self.sending_request} → Flee Assignment to {self.fleet_manager} - {self.driver} - {self.assigned_at}"
