from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound
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
        'status': openapi.Schema(type=openapi.TYPE_STRING, description="Statut de la demande", default="pending"),
    },
    required=['status']  # Champs obligatoires
)

form_parameters = [
    # openapi.Parameter('driver', openapi.IN_FORM, description="ID du chauffeur", required=True),
    openapi.Parameter('chief_fleet', openapi.IN_FORM, description="ID Chef client", type=openapi.TYPE_STRING),
    openapi.Parameter('status', openapi.IN_FORM, description="Status du demande", type=openapi.TYPE_STRING,
                      required=True, default="pending"),
]


# CRUD Chef & Driver Request
class DriverChiefRequestView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Demander d'intégration flotte",
        # manual_parameters=form_parameters,
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
            # Récupérer l'objet DriverChiefRequest
            request_obj = DriverChiefRequest.objects.get(pk=pk)

            # Vérifier les permissions
            if request_obj.driver.id != user.id and request_obj.chief_fleet.id != user.id:
                raise PermissionDenied("User unauthorized")

            return request_obj
        except DriverChiefRequest.DoesNotExist:
            raise NotFound("Request not found")

    @swagger_auto_schema(
        operation_description="Récupérer une demande spécifique",
        responses={
            200: openapi.Response("Details for request", DriverChiefRequestSerializer),
            403: openapi.Response("User unauthorized"),
            404: openapi.Response("Request not found"),
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
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Mettre à jour une demande",
        # manual_parameters=[
        #     openapi.Parameter('status', openapi.IN_FORM, description="Nouveau statut", type=openapi.TYPE_STRING,
        #                       required=True),
        # ],
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
        },
        tags=[tags]
    )
    def put(self, request, pk):
        try:
            # Récupérer l'objet via get_object
            request_obj = self.get_object(pk, request.user)

            # Seul le ChiefFleet peut mettre à jour le statut
            if request.user.role != 'chief':
                raise PermissionDenied("Only Chief fleet is authorized.")

            # Mettre à jour l'objet avec les données fournies
            serializer = DriverChiefRequestSerializer(request_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

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
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Gérer toute autre exception inattendue
            return Response({"error": "Error for deleting request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
