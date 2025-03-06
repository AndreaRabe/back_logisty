from rest_framework.response import Response

from apps.sendingRequest.models import SendingRequest
from apps.sendingRequest.serializers import DeliveryNoteSerializer


def sending_request_to_delivery_note(id_sending_request: int, ):
    """
    Cette fonction permet de creer un bon de commande correspondant au demande.
    """
    sending_request = SendingRequest.objects.values(
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
        # 'attached_files',  # il faut bien gerer ceci
        'special_conditions',
        'priority',
    ).get(pk=id_sending_request)

    serializer = DeliveryNoteSerializer(data=sending_request)

    if serializer.is_valid():
        new_instance = serializer.save()
        return new_instance.id
    else:
        print(serializer.errors)  # Afficher les erreurs dans la console
        return Response(serializer.errors, status=400)  # Retourner les erreurs dans la réponse
