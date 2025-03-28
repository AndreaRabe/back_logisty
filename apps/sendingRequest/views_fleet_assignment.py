from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.sendingRequest.models import SendingRequestFleetAssignment
from apps.sendingRequest.serializers import SendingRequestFleetAssignmentSerializer, \
    CancelSendingRequestFleetAssignmentSerializer
from apps.sendingRequest.utils import sending_request_to_delivery_note

# Views for Fleet assignment

tags = "Fleet Assignment"

body_parameters = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "sending_request": openapi.Schema(type=openapi.TYPE_STRING, description="ID Sending Request"),
        "driver": openapi.Schema(type=openapi.TYPE_STRING, description="ID Driver"),
        "truck": openapi.Schema(type=openapi.TYPE_STRING, description="ID Truck"),
    },
    required=["sending_request", "driver"],
)


class FleetAssignmentView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def verify_assignment(self, pk):
        return SendingRequestFleetAssignment.objects.get(sending_request=pk, status="assigned")

    @swagger_auto_schema(
        operation_description="Assigner un chef de flotte avec chauffeur a une demande",
        request_body=body_parameters,
        responses={
            201: openapi.Response("Assignment done successfully", SendingRequestFleetAssignmentSerializer),
            400: openapi.Response("Bad Request"),
            403: openapi.Response("User unauthorized"),
        },
        tags=[tags]
    )
    def post(self, request):
        try:
            chief_fleet = request.user
            if chief_fleet.role == "chief":
                data = request.data.copy()  # Copier les données pour les modifier
                data['fleet_manager'] = chief_fleet.id

                id_delivery_note = sending_request_to_delivery_note(data['sending_request'])
                data['delivery_note'] = id_delivery_note

                sending_req = self.verify_assignment(data['sending_request'])

                if sending_req:
                    return Response({"error": "Request already assigned"}, status=status.HTTP_400_BAD_REQUEST)

                serializer = SendingRequestFleetAssignmentSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "You must be a chief to perform this request"},
                                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Lister les demandes ou le chef son assigne",
        responses={
            200: openapi.Response("List of chief assignment", SendingRequestFleetAssignmentSerializer),
            403: openapi.Response("User unauthorized"),
        },
        tags=[tags]
    )
    def get(self, request):
        chief_fleet = request.user
        if chief_fleet.role == "chief":
            requests = SendingRequestFleetAssignment.objects.filter(fleet_manager=chief_fleet)
        else:
            return Response({"error": "You must be a chief to perform this request"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = SendingRequestFleetAssignmentSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FleetAssignmentDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get_obj(self, pk):
        try:
            return SendingRequestFleetAssignment.objects.get(pk=pk, fleet_manager=self.request.user)
        except SendingRequestFleetAssignment.DoesNotExist:
            raise NotFound("Request not found")

    @swagger_auto_schema(
        operation_description="Changer de chauffeur",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "driver": openapi.Schema(type=openapi.TYPE_STRING, description="ID Driver"),
            },
            required=["driver"]
        ),
        responses={
            200: openapi.Response("Update driver done", SendingRequestFleetAssignmentSerializer),
            400: openapi.Response("Bad request"),
            403: openapi.Response("User unauthorized"),
        },
        tags=[tags]
    )
    def put(self, request, pk):
        request_assignment = self.get_obj(pk)
        serializer = SendingRequestFleetAssignmentSerializer(request_assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Annuler le transport",
        responses={
            200: openapi.Response("Update assignment request done", SendingRequestFleetAssignmentSerializer),
            404: openapi.Response("Request not found"),
            500: openapi.Response("Internal server error"),
        },
        tags=[tags]
    )
    def post(self, request, pk):
        request_assignment = self.get_obj(pk)
        request_assignment.status = "cancelled"
        request_assignment.save()
        serializer = CancelSendingRequestFleetAssignmentSerializer(request_assignment)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
