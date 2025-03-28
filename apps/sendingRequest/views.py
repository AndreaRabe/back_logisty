from django.http import Http404
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
from ..invoice.views import invoice_sending_request_post

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
            description="Type of cargo being sent",
            enum=["container", "pallets_boxes", "bulk_fret", "vehicle", "animals", "furniture_tools", "other"]
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
            description="Priority level of the request",
            enum=["medium", "high"],
        ),
        'base_price': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            format=openapi.FORMAT_FLOAT,
            description="Base Price",
        ),
        'commission_rate': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            format=openapi.FORMAT_FLOAT,
            description="Commission Rate in percentage(20%, 25.2%, ...)"
        ),
        'total_price': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            format=openapi.FORMAT_FLOAT,
            description="Total montant a payer"
        ),
    },
    required=[
        'client', 'recipient_name', 'recipient_email', 'recipient_phone',
        'cargo_type', 'weight', 'dimensions', 'quantity',
        'pickup_location', 'pickup_date_time',
        'delivery_location', 'delivery_date_time', 'payment_method'
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
        user = request.user
        try:
            client = Member.objects.get(user_ptr=user)

        except Member.DoesNotExist:
            return Response({"error": "You must be a client to perform this request"}, status=status.HTTP_403_FORBIDDEN)

        if user.role == "client" or user.role == "company":
            data = request.data.copy()  # Copier les données pour les modifier
            data['client'] = client.id  # Ajouter l'ID du driver

            serializer = SendingRequestSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                invoice_sending_request_post(serializer.data)
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Relancer une demande annuler precedement (possibilite de mettre a jour les specifications)",
        request_body=body_parameters,
        responses={
            200: openapi.Response("Request relaunched"),
            403: openapi.Response("User unauthorized"),
            404: openapi.Response("Request not found"),
            500: openapi.Response("Internal Server Error"),
        },
        tags=[tags]

    )
    def post(self, request, pk):
        # Logique de payment ou l'user doit donner 20% du prix de depart pour relancer un demande qu'il a annuler

        sending_request = self.get_object(pk)
        if request.data:
            data = request.data.copy()
            data['status'] = 'pending'
            serializer = SendingRequestSerializer(sending_request, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            sending_request.status = "pending"
            sending_request.save()
            serializer = SendingRequestSerializer(sending_request)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a specific sending request",
        responses={
            200: openapi.Response("Request cancelled"),
            204: openapi.Response("Request deleted successfully"),
            403: openapi.Response("User unauthorized"),
            404: openapi.Response("Request not found"),
            500: openapi.Response("Internal Server Error"),
        },
        tags=[tags]
    )
    def delete(self, request, pk):
        sending_request = self.get_object(pk)
        # Pour supprimer un demande deja annule
        if sending_request and sending_request.status in ["cancelled", "rejected"]:
            sending_request.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif sending_request and sending_request.status == "in_progress":
            sending_request.status = "cancelled"
            sending_request.save()
            # Utiliser le sérialiseur pour formater les données
            serializer = SendingRequestSerializer(sending_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif sending_request.status in ["accepted", "in_progress"]:
            # logique pour la deduction de 20% de l'argent deja envoye et l'attente pour recevoire le retour de l'argent
            sending_request.status = "cancelled"
            sending_request.save()
            serializer = SendingRequestSerializer(sending_request)
            return Response(serializer.data, status=status.HTTP_200_OK)

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
                    enum=['accepted', 'rejected'],
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
        operation_description="Afficher la liste des demandes avec filtres optionnels",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filtrer les demandes par statut (ex: accepted, canceled)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: openapi.Response("List of sending request", SendingRequestSerializer),
            403: openapi.Response("User unauthorized"),
        },
        tags=[tags]
    )
    def get(self, request):
        valid_statuses = ['pending', 'accepted', 'canceled', 'completed', 'rejected', 'in_progress']
        status_filter = request.query_params.get('status', None)

        # Filtrer les demandes en fonction du statut
        if status_filter:
            # Si plusieurs statuts sont fournis (séparés par des virgules)
            statuses = status_filter.split(',')
            statuses = [stat for stat in statuses if stat in valid_statuses]
            if not statuses:
                return Response({"error": "Invalid status values"}, status=status.HTTP_400_BAD_REQUEST)
            send_requests = SendingRequest.objects.filter(status__in=statuses)
        else:
            # Si aucun filtre n'est fourni, retourner toutes les demandes
            send_requests = SendingRequest.objects.all()

        # Sérialiser les résultats
        serializer = SendingRequestSerializer(send_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChiefFleetSendingRequestDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Afficher la liste des demandes pas encore pris en charge",
        responses={
            200: openapi.Response("List of sending request", SendingRequestSerializer),
            403: openapi.Response("User unauthorized"),
        },
        tags=[tags]
    )
    def get(self, request):
        if request.user.role == "chief":
            send_requests = SendingRequest.objects.filter(status="accepted")
            serializer = SendingRequestSerializer(send_requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User unauthorized"}, status=status.HTTP_403_FORBIDDEN)
