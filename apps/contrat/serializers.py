from rest_framework import serializers

from apps.contrat.models import Contrat


class ContratSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrat
        fields = '__all__'
        read_only_fields = ["id", "contrat_date"]
