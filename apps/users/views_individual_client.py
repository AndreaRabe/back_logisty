import os

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import IndividualClient
from apps.users.serializers import IndividualClientSerializer

# The views for clientSerializer

tags = "Client Particulier"

body_parameters = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description="Adresse email"),
        'username': openapi.Schema(type=openapi.TYPE_STRING, description="Nom utilisateur"),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="Prénom client"),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="Nom client"),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description="Mot de passe"),
        'phone': openapi.Schema(type=openapi.TYPE_STRING, description="Numéro de téléphone"),
        'address': openapi.Schema(type=openapi.TYPE_STRING, description="Adresse"),
        'profile_pic': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.TYPE_FILE,
                                      description="Photo de profil"),
        'role': openapi.Schema(type=openapi.TYPE_STRING, default='client', description="Rôle"),
    },
    required=['email', 'last_name', 'password', 'phone', 'address']  # Champs obligatoires
)

form_parameters = [
    openapi.Parameter('email', openapi.IN_FORM, description="Adresse email", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('username', openapi.IN_FORM, description="Nom utilisateur", type=openapi.TYPE_STRING),
    openapi.Parameter('first_name', openapi.IN_FORM, description="Nom client", type=openapi.TYPE_STRING),
    openapi.Parameter('last_name', openapi.IN_FORM, description="Prenom client", type=openapi.TYPE_STRING,
                      required=True),
    openapi.Parameter('password', openapi.IN_FORM, description="Mot passe", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('phone', openapi.IN_FORM, description="Telephone", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('address', openapi.IN_FORM, description="Adresse", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('profile_pic', openapi.IN_FORM, description="Photo de profil", type=openapi.TYPE_FILE),
    openapi.Parameter('role', openapi.IN_FORM, description="Role", type=openapi.TYPE_STRING, default='client'),
]


# CRUD Client Particulier
class ClientParticulierView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Creer compte client particulier",
        # manual_parameters=form_parameters,
        request_body=body_parameters,
        responses={
            201: openapi.Response("Client created", IndividualClientSerializer),
            400: openapi.Response("Bad Request"),
        },
        tags=[tags]
    )
    def post(self, request):
        serializer = IndividualClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientParticulierProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Voir profil client particulier",
        responses={
            200: openapi.Response("Profile client", IndividualClientSerializer),
            400: openapi.Response("Bad Request"),
            404: openapi.Response('Client not Found')
        },
        tags=[tags]
    )
    def get(self, request):
        client = request.user
        if client:
            serializer = IndividualClientSerializer(IndividualClient.objects.get(user_ptr=client))
            if serializer.data:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Mettre a jour le profile client",
        # manual_parameters=form_parameters,
        request_body=body_parameters,
        responses={
            200: openapi.Response('Profile client updated', IndividualClientSerializer),
            400: openapi.Response('Bad Request'),
            403: openapi.Response('User unauthorized'),
            404: openapi.Response("Client not found"),
        },
        tags=[tags]
    )
    def put(self, request):
        client = request.user
        if client:
            client_id = request.data.get('id')
            if client_id and str(client.id) != client_id:
                return Response({"error": "User unauthorized"}, status=status.HTTP_403_FORBIDDEN)

            serializer = IndividualClientSerializer(client, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Supprimer compte client",
        responses={
            204: openapi.Response('Client deleted'),
            400: openapi.Response('Bad Request'),
            404: openapi.Response("Client not found"),
        },
        tags=[tags]
    )
    def delete(self, request):
        try:
            client = request.user
            if client:
                if client.profile_pic:
                    image_path = client.profile_pic.path
                    if os.path.exists(image_path):
                        os.remove(image_path)
                client.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ClientParticulierGetView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupérer tous les clients particuliers ou un client spécifique par ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING,
                                     description="ID du client particulier à récupérer (optionnel)"),
            },
        ),
        responses={
            200: openapi.Response("List of individual client", IndividualClientSerializer),
            400: openapi.Response("Bad Request"),
            404: openapi.Response("Individual Client not found"),
            500: openapi.Response("Internal Server Error")
        },
        tags=[tags]
    )
    def post(self, request):
        try:
            client_id = request.data.get('id')
            if client_id:
                try:
                    client = IndividualClient.objects.get(id=client_id)
                except IndividualClient.DoesNotExist:
                    return Response({'detail': "Individual Client not found"}, status=status.HTTP_404_NOT_FOUND)

                serializer = IndividualClientSerializer(client)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                drivers = IndividualClient.objects.all()
                serializer = IndividualClientSerializer(drivers, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
