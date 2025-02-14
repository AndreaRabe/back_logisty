# The views for ChiefFleetSerializer
import os

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import ChiefFleet
from apps.users.serializers import ChiefFleetSerializer

tags = "Chef de flotte"

body_parameters = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description="Adresse email"),
        'username': openapi.Schema(type=openapi.TYPE_STRING, description="Nom utilisateur"),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="Prénom chef de flotte"),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="Nom chef de flotte"),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description="Mot de passe"),
        'phone': openapi.Schema(type=openapi.TYPE_STRING, description="Numéro de téléphone"),
        'profile_pic': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.TYPE_FILE,
                                      description="Photo de profil"),
        'company_name': openapi.Schema(type=openapi.TYPE_STRING, description="Nom de la compagnie"),
        'company_address': openapi.Schema(type=openapi.TYPE_STRING, description="Adresse de la compagnie"),
        'role': openapi.Schema(type=openapi.TYPE_STRING, default='chief', description="Rôle"),
    },
    required=['email', 'last_name', 'password', 'phone', 'company_name', 'company_address']  # Champs obligatoires
)

form_parameters = [
    openapi.Parameter('email', openapi.IN_FORM, description="Adresse email", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('username', openapi.IN_FORM, description="Nom utilisateur", type=openapi.TYPE_STRING),
    openapi.Parameter('first_name', openapi.IN_FORM, description="Nom chef de flotte", type=openapi.TYPE_STRING),
    openapi.Parameter('last_name', openapi.IN_FORM, description="Prenom chef de flotte", type=openapi.TYPE_STRING,
                      required=True),
    openapi.Parameter('password', openapi.IN_FORM, description="Mot passe", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('phone', openapi.IN_FORM, description="Telephone", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('profile_pic', openapi.IN_FORM, description="Photo de profil", type=openapi.TYPE_FILE),
    openapi.Parameter('company_name', openapi.IN_FORM, description="Nom de la company", type=openapi.TYPE_STRING,
                      required=True),
    openapi.Parameter('company_address', openapi.IN_FORM, description="Adresse de la compagnie",
                      type=openapi.TYPE_STRING, required=True)
]


# CRUD Chef de flotte

class ChiefFleetView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Creer un compte chef de flotte",
        # manual_parameters=form_parameters,
        request_body=body_parameters,
        responses={
            201: openapi.Response("Chief Fleet created", ChiefFleetSerializer),
            400: openapi.Response("Bad Request")
        },
        tags=[tags]
    )
    def post(self, request):
        serializer = ChiefFleetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChiefFleetProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Voir profil Chef de flotte",
        responses={
            200: openapi.Response("Profile Chief Fleet", ChiefFleetSerializer),
            400: openapi.Response("Bad Request"),
            404: openapi.Response('Chief Fleet not Found')
        },
        tags=[tags]
    )
    def get(self, request):
        chief_fleet = request.user
        if chief_fleet:
            serializer = ChiefFleetSerializer(ChiefFleet.objects.get(user_ptr=chief_fleet))
            if serializer.data:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Voir la liste des chauffeurs",
        responses={
            200: openapi.Response("List Fleet", ChiefFleetSerializer),
            400: openapi.Response("Bad Request"),
            404: openapi.Response('No list driver')
        },
        tags=[tags]
    )
    def get_driver(self, request):
        chief_fleet = request.user
        if chief_fleet:
            serializer = ChiefFleetSerializer(ChiefFleet.objects.get(user_ptr=chief_fleet))
            if serializer.data:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Mettre a jour le profile chef de flotte",
        # manual_parameters=form_parameters,
        request_body=body_parameters,
        responses={
            200: openapi.Response('Profile Chief Fleet updated', ChiefFleetSerializer),
            400: openapi.Response('Bad Request'),
            403: openapi.Response('User unauthorized'),
            404: openapi.Response("Chief Fleet not found"),
        },
        tags=[tags]
    )
    def put(self, request):
        chief_fleet = request.user
        if chief_fleet:
            chief_fleet_id = request.data.get('id')
            if chief_fleet_id and str(chief_fleet.id) != chief_fleet_id:
                return Response({"error": "User unauthorized"}, status=status.HTTP_403_FORBIDDEN)

            serializer = ChiefFleetSerializer(chief_fleet, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Supprimer compte Chief Client",
        responses={
            204: openapi.Response('Chief Client deleted'),
            400: openapi.Response('Bad Request'),
            404: "Chief Client not found",
        },
        tags=[tags]
    )
    def delete(self, request):
        try:
            chief_fleet = request.user
            if chief_fleet:
                if chief_fleet.profile_pic:
                    image_path = chief_fleet.profile_pic.path
                    if os.path.exists(image_path):
                        os.remove(image_path)
                chief_fleet.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Chief Client not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChiefFleetGetView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupérer tous les chefs de flottes ou un chef de flotte spécifique par ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING,
                                     description="ID du chef de flotte à récupérer (optionnel)"),
            },
        ),
        responses={
            200: openapi.Response("List of Chief fleet", ChiefFleetSerializer),
            400: openapi.Response("Bad Request"),
            404: openapi.Response("Chief Fleet not found"),
            500: openapi.Response("Internal Server Error")
        },
        tags=[tags]
    )
    def post(self, request):
        try:
            chief_fleet_id = request.data.get('id')
            if chief_fleet_id:
                try:
                    chief_fleet = ChiefFleet.objects.get(id=chief_fleet_id)
                except ChiefFleet.DoesNotExist:
                    return Response({'detail': "Chief fleet not found"}, status=status.HTTP_404_NOT_FOUND)

                serializer = ChiefFleetSerializer(chief_fleet)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                drivers = ChiefFleet.objects.all()
                serializer = ChiefFleetSerializer(drivers, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
