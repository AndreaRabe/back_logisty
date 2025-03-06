from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Driver, DriverChiefRequest
from apps.users.serializers import DriverChiefRequestSerializer

# The views for chefDriver request

tags = "Chef & Driver Request"

body_parameters = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'chief_fleet': openapi.Schema(type=openapi.TYPE_STRING, description="ID Chef client"),
        'status': openapi.Schema(type=openapi.TYPE_STRING, description="Request Status", default="pending"),
    },
    required=['status']
)


class DriverChiefRequestView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Demander d'intégration une flotte",
        request_body=body_parameters,
        responses={
            201: openapi.Response("Request created", DriverChiefRequestSerializer),
            400: openapi.Response("Bad Request"),
            403: openapi.Response("You must a driver to perform this request")
        },
        tags=[tags]
    )
    def post(self, request):
        user = request.user
        try:
            driver = Driver.objects.get(user_ptr=user)
        except Driver.DoesNotExist:
            return Response({"error": "You must a driver to perform this request"}, status=status.HTTP_403_FORBIDDEN)

        # Ajouter l'ID du driver dans les données de la requête
        data = request.data.copy()  # Copier les données pour les modifier
        data['driver'] = driver.id  # Ajouter l'ID du driver

        # Sérialiser et valider les données
        serializer = DriverChiefRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Lister les demandes d'intégration",
        responses={
            200: openapi.Response("List of request", DriverChiefRequestSerializer),
            403: openapi.Response("User unauthorized"),
        },
        tags=[tags]
    )
    def get(self, request):
        user = request.user
        if user.role == 'driver':
            requests = DriverChiefRequest.objects.filter(driver=user)
        elif user.role == 'chief':
            requests = DriverChiefRequest.objects.filter(chief_fleet=user)
        else:
            return Response({"error": "User unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = DriverChiefRequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DriverChiefRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get_object(self, pk, user):
        try:
            if user.role == "driver":
                request_obj = DriverChiefRequest.objects.get(pk=pk, driver=user)
            elif user.role == "chief":
                request_obj = DriverChiefRequest.objects.get(pk=pk, chief_fleet=user)
            else:
                return Response("User unauthorized", status=status.HTTP_403_FORBIDDEN)

            return request_obj
        except DriverChiefRequest.DoesNotExist:
            return Response("Request not found", status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Récupérer une demande spécifique",
        responses={
            200: openapi.Response("Details for request", DriverChiefRequestSerializer),
            403: openapi.Response("User unauthorized"),
            404: openapi.Response("Request not found"),
            500: openapi.Response("Internal Server Error")
        },
        tags=[tags]
    )
    def get(self, request, pk):
        try:
            # Récupérer l'objet via get_object
            request_obj = self.get_object(pk, request.user)

            # Sérialiser les données
            serializer = DriverChiefRequestSerializer(request_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Mettre à jour une demande",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, description="Statut de la demande",
                                         default="pending"),
            },
            required=['status']),
        responses={
            200: openapi.Response("Update request done", DriverChiefRequestSerializer),
            400: openapi.Response("Bad request"),
            403: openapi.Response("User unauthorized"),
            500: openapi.Response("Internal Server Error")
        },
        tags=[tags]
    )
    def put(self, request, pk):
        try:
            request_obj = self.get_object(pk, request.user)

            if request.user.role != 'chief':
                raise PermissionDenied("Only Chief fleet is authorized.")

            serializer = DriverChiefRequestSerializer(request_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Supprimer une demande",
        responses={
            204: openapi.Response("Request deleted"),
            403: openapi.Response("User unauthorized"),
            404: openapi.Response("Request not found"),
            500: openapi.Response("Internal server error"),
        },
        tags=[tags]
    )
    def delete(self, request, pk):
        try:
            # Récupérer l'objet via get_object
            request_obj = self.get_object(pk, request.user)

            # Supprimer l'objet
            request_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChiefManagementAssignmentView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get_obj(self):
        try:
            return DriverChiefRequest.objects.get(fleet_manager=self.request.user)
        except DriverChiefRequest.DoesNotExist:
            return Response("No request found", status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Supprimer tout les demandes ou le chef est assigne",
        responses={
            204: openapi.Response("Deleted successfully"),
            403: openapi.Response("User unauthorized"),
            404: openapi.Response("No request found"),
            500: openapi.Response("Internal server error"),
        }
    )
    def delete(self, request):
        try:
            if request.user.role == "chief":
                request_assignment = self.get_obj()
                request_assignment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"error": "You must be a chief to perform this request"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
