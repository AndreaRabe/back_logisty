from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subscription.models import SubscriptionPlan
from apps.subscription.serializers import SubscriptionPlanSerializer

tags = "Subscription plan"

body_parameters = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "name": openapi.Schema(
            type=openapi.TYPE_STRING,
            max_length=100,
            description="Name of the plan (e.g., Basic, Pro, Enterprise)"
        ),
        "description": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Detailed description of the plan"
        ),
        "price": openapi.Schema(
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
            description="Price of the plan (e.g., monthly or annual fee)"
        ),
        "duration_month": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="Duration of the plan in month"
        ),
        "features": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="Features included in the plan as a JSON object (e.g., {'priority_support': True})"
        ),
    }
)


class SubscriptionPlanView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Ajouter un nouveua plan d'abonnement",
        request_body=body_parameters,
        responses={
            201: openapi.Response("Request created successfully", SubscriptionPlanSerializer),
            400: openapi.Response("Bad Request"),
        },
        tags=[tags]
    )
    def post(self, request):
        data = request.data
        serializer = SubscriptionPlanSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionPlanListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Afficher la liste des plans d'abonnement",
        responses={
            200: openapi.Response("List of subscription plan", SubscriptionPlanSerializer),
            500: openapi.Response("Internal Server Error"),
        },
        tags=[tags]
    )
    def get(self, request):
        try:
            subscription_plans = SubscriptionPlan.objects.all()
            serializer = SubscriptionPlanSerializer(subscription_plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubscriptionPlanDetailsView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser]

    def get_object(self, pk):
        try:
            return SubscriptionPlan.objects.get(pk=pk)
        except SubscriptionPlan.DoesNotExist:
            raise NotFound("Subscription plan not found")

    @swagger_auto_schema(
        operation_description="Editer un abonement",
        request_body=body_parameters,
        responses={
            201: openapi.Response("Subscription plan updated successfully", SubscriptionPlanSerializer),
            400: openapi.Response("Bad Request"),
            404: openapi.Response("Subscription plan not found"),
        },
        tags=[tags]
    )
    def put(self, request, pk):
        subscription_plan = self.get_object(pk)
        serializer = SubscriptionPlanSerializer(subscription_plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Supprimer un abonement",
        responses={
            200: openapi.Response("Subscription plan deactivated", SubscriptionPlanSerializer),
            500: openapi.Response("Internal Server Error"),
        },
        tags=[tags]
    )
    def delete(self, request, pk):
        try:
            subscription_plan = self.get_object(pk)
            subscription_plan.is_active = False
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
