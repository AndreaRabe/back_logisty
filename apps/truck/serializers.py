from rest_framework import serializers

from apps.truck.models import Truck


class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
