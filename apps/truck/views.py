from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.truck.models import Truck
from apps.truck.serializers import TruckSerializer

# Create your views here.

tags = "Trucks"

body_parameters = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "license_plate": openapi.Schema(type=openapi.TYPE_STRING, max_length=10, description="Truck Immatriculation"),
        "brand": openapi.Schema(type=openapi.TYPE_STRING, max_length=20, description="Truck Brand"),
        "model": openapi.Schema(type=openapi.TYPE_STRING, max_length=20, description="Truck Model"),
        "year": openapi.Schema(type=openapi.TYPE_INTEGER, max_length=4, description="Truck Year"),
        "color": openapi.Schema(type=openapi.TYPE_STRING, max_length=10, description="Truck Color"),
        "last_maintenance_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
                                                description="Last date Truck Maintenance"),
        "next_maintenance_due": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
                                               description="Next Date Truck Maintenance"),
        "max_load_capacity": openapi.Schema(type=openapi.FORMAT_FLOAT, description="Max Load Capacity"),
        "insurance": openapi.Schema(type=openapi.TYPE_STRING, max_length=10, description="Insurance information"),
        "status": openapi.Schema(type=openapi.TYPE_STRING, description="Truck Status",
                                 enum=["available", "maintenance", "on mission"]),
        "last_service_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
                                            description="Date for the last service"),
        "mileage": openapi.Schema(type=openapi.TYPE_INTEGER, max_length=10, description="Mileage"),
        "notes": openapi.Schema(type=openapi.TYPE_STRING, description="Other specification"),
    }
)


def get_object_truck(pk):
    try:
        return Truck.objects.get(pk=pk, is_active=True)
    except Truck.DoesNotExist:
        raise Http404("Truck not found")


class TruckView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Ajouter un camion dans la base de donnees",
        request_body=body_parameters,
        responses={
            201: openapi.Response("Truck added"),
            400: openapi.Response("Bad Request"),
            403: openapi.Response("Forbidden (you must be a chief)"),
            500: openapi.Response("Internal Server Error"),
        },
        tags=[tags]
    )
    def post(self, request):
        try:
            if request.user.role == "chief":
                data = request.data.copy()
                data["chief_fleet"] = request.user.id
                serializer = TruckSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TruckDetail(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Update a truck information",
        request_body=body_parameters,
        responses={
            200: openapi.Response("Truck updated"),
            400: openapi.Response("Bad Request"),
        },
        tags=[tags]
    )
    def put(self, request, pk):
        truck = get_object_truck(pk)
        serializer = TruckSerializer(truck, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a truck information",
        responses={
            200: openapi.Response("Truck deleted"),
            400: openapi.Response("Bad Request"),
            500: openapi.Response("Internal Server Error"),
        },
        tags=[tags]
    )
    def delete(self, request, pk):
        try:
            truck = get_object_truck(pk)
            truck.is_active = False
            truck.save()
            return Response({"message": "Truck deleted successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TruckListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Recuperer la liste des trucks",
        manual_parameters=[
            openapi.Parameter(
                "truck_id",
                openapi.IN_QUERY,
                description="ID du camion à récupérer (optionnel)",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response("List of truck"),
            500: openapi.Response("Internal Server Error"),
        },
        tags=[tags]
    )
    def get(self, request):
        try:
            truck_id = request.query_params.get("truck_id")
            if truck_id:
                truck = get_object_truck(truck_id)
                serializer = TruckSerializer(truck)
            else:
                trucks = Truck.objects.filter(is_active=True)
                serializer = TruckSerializer(trucks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
