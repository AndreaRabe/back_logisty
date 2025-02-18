from rest_framework import serializers

from apps.users.serializers import MemberSerializer
from .models import SendingRequest


class SendingRequestSerializer(serializers.ModelSerializer):
    client_details = MemberSerializer(source='client', read_only=True)

    class Meta:
        model = SendingRequest
        fields = [
            'id',
            'client',
            'recipient_name',
            'recipient_email',
            'recipient_phone',
            'cargo_type',
            'weight',
            'dimensions',
            'quantity',
            'pickup_location',
            'pickup_date_time',
            'delivery_location',
            'delivery_date_time',
            'additional_details',
            'attached_files',
            'special_conditions',
            'priority',
            'payment_method',
            'request_date',
            'status',
            'client_details'
        ]
        read_only_fields = ['id', 'request_date', 'status', 'client_details']


class AdminSendingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendingRequest
        fields = ['status']  # Seul le champ `status` est modifiable
