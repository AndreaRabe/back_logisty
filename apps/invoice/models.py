from django.db import models

from apps.sendingRequest.models import SendingRequest
from apps.subscription.models import Subscription
from apps.users.models import Member

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('canceled', 'Canceled'),
]

PAYMENT_METHOD_CHOICES = [
    ('mobile_money', 'Mobile Money'),
    ('bank_transfer', 'Bank Transfer'),
    ('cash', 'Cash'),
]


class SubscriptionInvoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    client = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="subscription_invoices")
    sub_plan = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)

    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='mobile_money')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='paid')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.invoice_number:
            self.invoice_number = f"SUB-INV-{self.pk:04d}"
            super().save(update_fields=['invoice_number'])

    def __str__(self):
        return f"Subscription Invoice {self.invoice_number} - {self.total_ttc} Ar"


class SendingRequestInvoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    client = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="sending_request_invoices")
    sending_request = models.ForeignKey(SendingRequest, on_delete=models.SET_NULL, null=True, blank=True)

    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='mobile_money')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='paid')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # D'abord on sauvegarde pour obtenir un ID
        if not self.invoice_number:
            self.invoice_number = f"REQ-INV-{self.pk:04d}"  # Utiliser pk au lieu de id
            super().save(update_fields=['invoice_number'])  # Mise à jour sans déclencher une boucle

    def __str__(self):
        return f"Sending Request Invoice {self.invoice_number} - {self.total_ttc} Ar"
