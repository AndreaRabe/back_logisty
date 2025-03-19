from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contrat.models import Contrat
from apps.contrat.serializers import ContratSerializer

# Create your views here.
tags = "Contrat"

body_parameters = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "chief_fleet": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Chief fleet ID",
        ),
        "contract_terms": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Contract terms",
        ),
        "subscription_fee": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            format=openapi.FORMAT_DECIMAL,
            description="Subscription fee (price in MGA",
        ),
        "duration": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="Contract duration (in years)",
        ),
        "signature_details": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Signature details (name function date)",
        ),
    },
    required=["chief_fleet", "contract_terms", "subscription_fee", "duration"],
)


def get_contrat(pk):
    try:
        return Contrat.objects.get(pk=pk)
    except Contrat.DoesNotExist:
        raise NotFound("Contrat not found")


class ContratView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Creer un contrat pour un nouveau chef de flotte",
        request_body=body_parameters,
        responses={
            201: openapi.Response("Contract created", ContratSerializer),
            400: openapi.Response("Bad Request"),
            500: openapi.Response("Internal Server Error"),
        }
    )
    def post(self, request):
        try:
            serializer = ContratSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContratDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Recuperer un contrat",
        responses={
            200: openapi.Response("Contract details", ContratSerializer),
            404: openapi.Response("Contract not found"),
        }
    )
    def get(self, request, pk):
        contrat = get_contrat(pk)

        if contrat:
            serializer = ContratSerializer(contrat)
            if serializer.data:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Mettre a jour un contrat",
        request_body=body_parameters,
        responses={
            200: openapi.Response("Contract Updated", ContratSerializer),
            400: openapi.Response("Bad Request"),
            404: openapi.Response("Contract not found"),
            500: openapi.Response("Internal Server Error"),
        }
    )
    def put(self, request, pk):
        try:
            contrat = get_contrat(pk)
            if contrat:
                serializer = ContratSerializer(contrat, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Supprimer un contrat",
        responses={
            204: openapi.Response("Contrat deleted", ContratSerializer),
            404: openapi.Response("Contrat not found"),
            500: openapi.Response("Internal Server Error"),
        }
    )
    def delete(self, request, pk):
        try:
            contrat = get_contrat(pk)
            if contrat:
                contrat.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
