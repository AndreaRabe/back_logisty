from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Member
from .models import SendingRequest
from .serializers import SendingRequestSerializer, AdminSendingRequestSerializer

# Views for Sending Request

tags = "Sending Requests"

body_parameters = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'recipient_name': openapi.Schema(
            type=openapi.TYPE_STRING,
            max_length=150,
            description="Name of the recipient"
        ),
        'recipient_email': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
            description="Email address of the recipient"
        ),
        'recipient_phone': openapi.Schema(
            type=openapi.TYPE_STRING,
            max_length=15,
            description="Phone number of the recipient"
        ),

        # Détails du colis (Cargo Details)
        'cargo_type': openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Type of cargo being sent"
        ),
        'weight': openapi.Schema(
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
            description="Weight of the cargo in kg"
        ),
        'dimensions': openapi.Schema(
            type=openapi.TYPE_STRING,
            max_length=100,
            description="Dimensions of the cargo in LxWxH format (e.g., 100x50x30 cm)"
        ),
        'quantity': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="Number of items or quantity of cargo"
        ),

        # Lieu, date et heure de récupération (Pickup Details)
        'pickup_location': openapi.Schema(
            type=openapi.TYPE_STRING,
            max_length=100,
            description="Location where the cargo will be picked up"
        ),
        'pickup_date_time': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            description="Date and time of pickup"
        ),

        # Lieu, date et heure de livraison (Delivery Details)
        'delivery_location': openapi.Schema(
            type=openapi.TYPE_STRING,
            max_length=100,
            description="Location where the cargo will be delivered"
        ),
        'delivery_date_time': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            description="Date and time of delivery"
        ),

        # Autres spécifications détaillées (Additional Specifications)
        'additional_details': openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Additional details about the cargo (e.g., perishable goods, fragile items)",
            nullable=True
        ),

        # Photos ou documents joints (Attached Files)
        'attached_files': openapi.Schema(
            type=openapi.TYPE_FILE,
            description="Attached files related to the request",
            nullable=True
        ),

        # Conditions spéciales (Special Conditions)
        'special_conditions': openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Special conditions for handling the cargo (e.g., refrigeration required)",
            nullable=True
        ),

        # Priorité de la demande (Request Priority)
        'priority': openapi.Schema(
            type=openapi.TYPE_STRING,
            default='medium',
            description="Priority level of the request"
        ),

        # Mode de paiement (Payment Method)
        'payment_method': openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Payment method for the request",
            nullable=True
        ),
    },
    required=[
        'client', 'recipient_name', 'recipient_email', 'recipient_phone',
        'cargo_type', 'weight', 'dimensions', 'quantity',
        'pickup_location', 'pickup_date_time',
        'delivery_location', 'delivery_date_time'
    ]
)


class SendingRequestView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Rediger un formulaire pour la demande d'envoye",
        request_body=body_parameters,
        responses={
            201: openapi.Response("Request created successfully", SendingRequestSerializer),
            400: openapi.Response("Bad Request"),
            403: openapi.Response("User unauthorized"),
        },
        tags=[tags]
    )
    def post(self, request):
        try:
            client = Member.objects.get(user_ptr=request.user)

        except Member.DoesNotExist:
            return Response({"error": "You must be a client to perform this request"}, status=status.HTTP_403_FORBIDDEN)

        user = request.user
        if user.role == "client" or user.role == "company":
            data = request.data.copy()  # Copier les données pour les modifier
            data['client'] = client.id  # Ajouter l'ID du driver

            serializer = SendingRequestSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "You must be a client to perform this request"}, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        operation_description="Lister les demandes envoyes",
        responses={
            200: openapi.Response("List of sending request", SendingRequestSerializer),
            403: openapi.Response("User unauthorized"),
        },
        tags=[tags]
    )
    def get(self, request):
        user = request.user
        if user.role == 'company':
            requests = SendingRequest.objects.filter(client=user)
        elif user.role == 'client':
            requests = SendingRequest.objects.filter(client=user)
        else:
            return Response({"error": "User unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = SendingRequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendingRequestDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get_object(self, pk):
        try:
            return SendingRequest.objects.get(pk=pk, client=self.request.user)
        except SendingRequest.DoesNotExist:
            raise NotFound("Request not found")

    @swagger_auto_schema(
        operation_description="Recuperer un demande specifique",
        responses={
            200: openapi.Response("Details for request", SendingRequestSerializer),
            403: openapi.Response("User unauthorized"),
            404: openapi.Response("Request not found"),
        },
        tags=[tags]
    )
    def get(self, request, pk):
        try:
            request_obj = self.get_object(pk)
            serializer = SendingRequestSerializer(request_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Mettre a jour demande",
        request_body=body_parameters,
        responses={
            200: openapi.Response("Update request done", SendingRequestSerializer),
            400: openapi.Response("Bad request"),
            403: openapi.Response("User unauthorized"),
        },
        tags=[tags]
    )
    def put(self, request, pk):
        sending_request = self.get_object(pk)
        data = {**request.data, 'client': request.user.id}
        serializer = SendingRequestSerializer(sending_request, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a specific sending request",
        responses={
            204: openapi.Response("Request deleted successfully"),
            403: openapi.Response("User unauthorized"),
            404: openapi.Response("Request not found"),
            500: openapi.Response("Internal Server Error"),
        },
        tags=[tags]
    )
    def delete(self, request, pk):
        sending_request = self.get_object(pk)
        if sending_request:
            sending_request.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": f"Error for deleting request"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminSendingRequestUpdateView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser]

    def get_object(self, pk):
        try:
            return SendingRequest.objects.get(pk=pk)
        except SendingRequest.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_description="Mettre à jour le status d'une demande",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['pending', 'in_progress', 'completed', 'cancelled', 'rejected'],
                    description="New status for the sending request")
            }),
        responses={
            200: openapi.Response("Update request done", AdminSendingRequestSerializer),
            400: openapi.Response("Bad request"),
        },
        tags=[tags]
    )
    def put(self, request, pk):
        sending_request = self.get_object(pk)
        serializer = AdminSendingRequestSerializer(sending_request, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminSendingRequestDetailsView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Afficher la liste des demandes",
        responses={
            200: openapi.Response("List of sending request", SendingRequestSerializer),
            403: openapi.Response("User unauthorized"),
        },
        tags=[tags]
    )
    def get(self, request):
        send_requests = SendingRequest.objects.all()
        serializer = SendingRequestSerializer(send_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
