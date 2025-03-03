from rest_framework import serializers

from apps.invoice.models import SendingRequestInvoice, SubscriptionInvoice
from apps.subscription.serializers import SubscriptionSerializer
from apps.users.serializers import MemberSerializer


class SendingRequestInvoiceSerializer(serializers.ModelSerializer):
    client_details = MemberSerializer(source="client", read_only=True)
    sub_plan_details = SubscriptionSerializer(source="sub_plan", read_only=True)

    class Meta:
        model = SendingRequestInvoice
        fields = [
            'id',
            'invoice_number',
            'client',
            'sending_request',
            'total_ttc',
            'payment_method',
            'status',
            'created_at',
            'client_details',
            'sub_plan_details',
        ]
        read_only_fields = ['id', 'invoice_number',
                            'created_at', 'client_details',
                            'sub_plan_details', ]


class SubscriptionInvoiceSerializer(serializers.ModelSerializer):
    client_details = MemberSerializer(source="client", read_only=True)
    sub_plan_details = SubscriptionSerializer(source="sub_plan", read_only=True)

    class Meta:
        model = SubscriptionInvoice
        fields = [
            'id',
            'invoice_number',
            'client',
            'sub_plan',
            'total_ttc',
            'payment_method',
            'status',
            'created_at',
            'client_details',
            'sub_plan_details',
        ]
        read_only_fields = ['id', 'invoice_number',
                            'created_at', 'status', 'client_details',
                            'sub_plan_details', ]
