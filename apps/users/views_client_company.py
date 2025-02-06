import os

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import ClientCompanySerializer

# The views for ClientCompanySerializer

tags = "Entreprise Client"

form_parameters = [
    openapi.Parameter('email', openapi.IN_FORM, description="Adresse email", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('username', openapi.IN_FORM, description="Nom utilisateur", type=openapi.TYPE_STRING),
    openapi.Parameter('first_name', openapi.IN_FORM, description="Nom client", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('last_name', openapi.IN_FORM, description="Prenom client", type=openapi.TYPE_STRING,
                      required=True),
    openapi.Parameter('password', openapi.IN_FORM, description="Mot passe", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('phone', openapi.IN_FORM, description="Telephone", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('address', openapi.IN_FORM, description="Adresse", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('profile_pic', openapi.IN_FORM, description="Photo de profil", type=openapi.TYPE_FILE),
    openapi.Parameter('role', openapi.IN_FORM, description="Role", type=openapi.TYPE_STRING, default='company'),
    openapi.Parameter('company_name', openapi.IN_FORM, description="Nom compagnie", type=openapi.TYPE_STRING,
                      required=True),
    openapi.Parameter('industry', openapi.IN_FORM, description="Secteur d'activite", type=openapi.TYPE_STRING,
                      required=True),
]


# CRUD Client Company
class ClientCompanyView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="Creer compte entreprise client",
        manual_parameters=form_parameters,
        responses={
            201: openapi.Response("Client company account created", ClientCompanySerializer),
            400: openapi.Response("Bad Request"),
        },
        tags=[tags]
    )
    def post(self, request):
        serializer = ClientCompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientCompanyProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Voir profil entreprise client",
        responses={
            200: openapi.Response("Profile Client company", ClientCompanySerializer),
            400: openapi.Response("Bad Request"),
            404: openapi.Response('Client company not Found')
        },
        tags=[tags]
    )
    def get(self, request):
        client_company = request.user
        if client_company:
            serializer = ClientCompanySerializer(client_company)
            if serializer.data:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Mettre a jour le profile entreprise client",
        manual_parameters=form_parameters,
        responses={
            200: openapi.Response('Client company updated', ClientCompanySerializer),
            400: openapi.Response('Bad Request'),
            403: openapi.Response('User unauthorized'),
            404: "Client company not found",
        },
        tags=[tags]
    )
    def put(self, request):
        client_company = request.user
        if client_company:
            client_company_id = request.data.get('id')
            if client_company_id and str(client_company.id) != client_company_id:
                return Response({"error": "User unauthorized"}, status=status.HTTP_403_FORBIDDEN)

            serializer = ClientCompanySerializer(client_company, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Supprimer compte entreprise client",
        responses={
            204: openapi.Response('Client company deleted'),
            400: openapi.Response('Bad Request'),
            404: "Client company not found",
        },
        tags=[tags]
    )
    def delete(self, request):
        try:
            client_company = request.user
            if client_company:
                if client_company.profile_pic:
                    image_path = client_company.profile_pic.path
                    if os.path.exists(image_path):
                        os.remove(image_path)
                client_company.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Client company not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
