from django.db import models

from apps.users.models import ChiefFleet


# Create your models here.
class Contrat(models.Model):
    chief_fleet = models.ForeignKey(ChiefFleet, on_delete=models.CASCADE, related_name='contrats')
    contract_terms = models.TextField()
    subscription_fee = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()  # en annee
    signature_details = models.CharField(null=True, blank=True)  # Infos de signature (JSON)
    contrat_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Chief Fleet : {self.chief_fleet} - conditions {self.contract_terms} - duration {self.duration}"
