import os

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import DriverSerializer

# The views for driverSerializer
tags = "Chauffeur"

form_parameters = [
    openapi.Parameter('email', openapi.IN_FORM, description="Adresse email", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('username', openapi.IN_FORM, description="Nom utilisateur", type=openapi.TYPE_STRING),
    openapi.Parameter('first_name', openapi.IN_FORM, description="Nom chauffeur", type=openapi.TYPE_STRING,
                      required=True),
    openapi.Parameter('last_name', openapi.IN_FORM, description="Prenom chauffeur", type=openapi.TYPE_STRING,
                      required=True),
    openapi.Parameter('password', openapi.IN_FORM, description="Mot passe", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('phone', openapi.IN_FORM, description="Telephone", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('address', openapi.IN_FORM, description="Adresse", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('profile_pic', openapi.IN_FORM, description="Photo de profil", type=openapi.TYPE_FILE),
    openapi.Parameter('role', openapi.IN_FORM, description="Role", type=openapi.TYPE_STRING, default='driver'),
    openapi.Parameter('driving_license', openapi.IN_FORM, description="Photo permis de conduire",
                      type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('experience', openapi.IN_FORM, description="Annee d'experience", type=openapi.TYPE_STRING,
                      required=True),
]


# CRUD Driver
class DriverView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Creer compte Chauffeur",
        manual_parameters=form_parameters,
        responses={
            201: openapi.Response("Driver created", DriverSerializer),
            400: openapi.Response("Bad Request"),
        },
        tags=[tags]
    )
    def post(self, request):
        serializer = DriverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Voir profil Chauffeur",
        responses={
            200: openapi.Response("Profile Driver", DriverSerializer),
            400: openapi.Response("Bad Request"),
            404: openapi.Response('Client not Found')
        },
        tags=[tags]
    )
    def get(self, request):
        driver = request.user
        if driver:
            serializer = DriverSerializer(driver)
            if serializer.data:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Mettre a jour le profile chauffeur",
        manual_parameters=form_parameters,
        responses={
            200: openapi.Response('Profile driver updated', DriverSerializer),
            400: openapi.Response('Bad Request'),
            403: openapi.Response('User unauthorized'),
            404: "driver not found",
        },
        tags=[tags]
    )
    def put(self, request):
        driver = request.user
        if driver:
            driver_id = request.data.get('id')
            if driver_id and str(driver.id) != driver_id:
                return Response({"error": "User unauthorized"}, status=status.HTTP_403_FORBIDDEN)

            serializer = DriverSerializer(driver, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Supprimer compte Chauffeur",
        responses={
            204: openapi.Response('driver deleted'),
            400: openapi.Response('Bad Request'),
            404: "driver not found",
        },
        tags=[tags]
    )
    def delete(self, request):
        try:
            driver = request.user
            if driver:
                if driver.profile_pic:
                    image_path = driver.profile_pic.path
                    if os.path.exists(image_path):
                        os.remove(image_path)
                driver.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
