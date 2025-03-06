from rest_framework import serializers

from apps.users.serializers import MemberSerializer
from .models import SendingRequest, SendingRequestFleetAssignment, DeliveryNote
from ..truck.serializers import TruckSerializer


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
            'base_price',
            'commission_rate',
            'total_price',
            'request_date',
            'status',
            'client_details'
        ]
        read_only_fields = ['id', 'request_date', 'status', 'client_details']


class AdminSendingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendingRequest
        fields = ['status']  # Seul le champ `status` est modifiable


class CancelSendingRequestFleetAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendingRequestFleetAssignment
        fields = ["status"]


class DeliveryNoteSerializer(serializers.ModelSerializer):
    client_details = MemberSerializer(source='client', read_only=True)

    class Meta:
        model = DeliveryNote
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
            'request_date',
            'status',
            'client_details'
        ]
        read_only_fields = ['id', 'request_date', 'status', 'client_details']


class SendingRequestFleetAssignmentSerializer(serializers.ModelSerializer):
    driver_details = MemberSerializer(source='driver', read_only=True)
    sending_request_details = SendingRequestSerializer(source='sending_request', read_only=True)
    delivery_note_details = DeliveryNoteSerializer(source='delivery_note', read_only=True)
    truck_details = TruckSerializer(source='truck', read_only=True)

    class Meta:
        model = SendingRequestFleetAssignment
        fields = ['id',
                  'sending_request',
                  'fleet_manager',
                  'driver',
                  'truck',
                  'delivery_note',
                  'sending_request_details',
                  'driver_details',
                  'delivery_note_details',
                  'truck_details',
                  'assigned_at',
                  'status']
        read_only_fields = ['id', 'driver_details', 'status', 'sending_request_details', 'truck_details',
                            'delivery_note_details', 'assigned_at']
