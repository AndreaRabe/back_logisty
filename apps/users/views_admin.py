import os

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import AdminSerializer

# The views for adminSerializer

tags = "Admin"

form_parameters = [
    openapi.Parameter('email', openapi.IN_FORM, description="Adresse email", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('username', openapi.IN_FORM, description="Nom utilisateur", type=openapi.TYPE_STRING),
    openapi.Parameter('first_name', openapi.IN_FORM, description="Nom admin", type=openapi.TYPE_STRING),
    openapi.Parameter('last_name', openapi.IN_FORM, description="Prenom admin", type=openapi.TYPE_STRING),
    openapi.Parameter('password', openapi.IN_FORM, description="Mot de passe", type=openapi.TYPE_STRING,
                      required=True),
    openapi.Parameter('phone', openapi.IN_FORM, description="Telephone", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('profile_pic', openapi.IN_FORM, description="Photo de profil", type=openapi.TYPE_FILE),
    openapi.Parameter('role', openapi.IN_FORM, description="Role", type=openapi.TYPE_STRING, default='admin'),
]


# CRUD Admin
class AdminView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Creer compte admin",
        manual_parameters=form_parameters,
        responses={
            201: openapi.Response('Admin created', AdminSerializer),
            400: openapi.Response('Bad Request'),
        },
        tags=[tags]
    )
    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Voir profil admin",
        responses={
            200: openapi.Response('Profile Admin', AdminSerializer),
            400: openapi.Response('Bad Request'),
            404: 'Admin not found',
        },
        tags=[tags]
    )
    def get(self, request):
        admin = request.user
        if admin:
            serializer = AdminSerializer(admin)
            if serializer.data:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Mettre a jour le profile admin",
        manual_parameters=form_parameters,
        responses={
            200: openapi.Response('Profile admin updated', AdminSerializer),
            400: openapi.Response('Bad Request'),
            403: openapi.Response('User unauthorized'),
            404: "Admin not found",
        },
        tags=[tags]
    )
    def put(self, request):
        admin = request.user
        if admin:
            admin_id = request.data.get('id')
            if admin_id and str(admin.id) != admin_id:
                return Response(
                    {"error": "User unauthorized"},
                    status=status.HTTP_403_FORBIDDEN)

            serializer = AdminSerializer(admin, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Supprimer compte admin",
        responses={
            200: openapi.Response('Admin deleted'),
            400: openapi.Response('Bad Request'),
            404: "Admin not found",
        },
        tags=[tags]
    )
    def delete(self, request):
        try:
            admin = request.user
            if admin:
                if admin.profile_pic:
                    image_path = admin.profile_pic.path
                    if os.path.exists(image_path):
                        os.remove(image_path)
                admin.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
