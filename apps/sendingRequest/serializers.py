from rest_framework import serializers

from apps.users.serializers import MemberSerializer
from .models import SendingRequest, SendingRequestFleetAssignment


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


class SendingRequestFleetAssignmentSerializer(serializers.ModelSerializer):
    driver_details = MemberSerializer(source='driver', read_only=True)
    sending_request_details = SendingRequestSerializer(source='sending_request', read_only=True)

    class Meta:
        model = SendingRequestFleetAssignment
        fields = ['id', 'sending_request', 'fleet_manager', 'driver', 'sending_request_details', 'driver_details',
                  'assigned_at', 'status']
        read_only_fields = ['id', 'driver_details', 'status', 'sending_request_details']


class CancelSendingRequestFleetAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendingRequestFleetAssignment
        fields = ["status"]
