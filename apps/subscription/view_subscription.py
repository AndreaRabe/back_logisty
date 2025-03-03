from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.invoice.views import subscription_request_post
from apps.subscription.models import Subscription, SubscriptionPlan
from apps.subscription.serializers import SubscriptionSerializer

tags = "Subscription"

body_parameters = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "sub_plan": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Id of subscription plan"
        ),
        # "start_date": openapi.Schema(
        #     type=openapi.TYPE_STRING,
        #     format=openapi.FORMAT_DATE,
        #     description="Subscription start date",
        # ),
        "status": openapi.Schema(
            type=openapi.TYPE_STRING,
            default="active",
            description="Status of subscription",
            enum=['active', 'expired', 'cancelled']
        )
    }
)


def get_user(request):
    if request.user.role in ["client", "company"]:
        return request.user
    else:
        raise PermissionDenied("You must be a client or company to perform this request")


def get_object(request, pk):
    try:
        return Subscription.objects.get(pk=pk, client=request.user)
    except Subscription.DoesNotExist:
        raise Http404("Subscription not found")


def get_subscription_plan(pk):
    return SubscriptionPlan.objects.get(pk=pk)


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Effectuer une abonnement",
        request_body=body_parameters,
        responses={
            201: openapi.Response("Subscription done", SubscriptionSerializer),
            400: openapi.Response("Bad Request"),
            403: openapi.Response("User unauthorized")
        },
        tags=[tags]
    )
    def post(self, request):
        try:
            # Vérifier si l'utilisateur a déjà un abonnement actif
            current_subscription = Subscription.objects.get(client=request.user, status="active")

            if current_subscription.status == "active":
                return Response({"error": "You already have an active subscription"},
                                status=status.HTTP_400_BAD_REQUEST)

        except Subscription.DoesNotExist:
            pass
        user = get_user(request)
        data = request.data.copy()
        data['client'] = user.id

        serializer = SubscriptionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            subscription_plan = get_subscription_plan(data["sub_plan"])
            subscription_request_post(serializer.data, subscription_plan.price)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Afficher l'abonnement en cours",
        responses={
            200: openapi.Response("Subscription plan", SubscriptionSerializer),
            204: openapi.Response("You have no subscription", SubscriptionSerializer),
            500: openapi.Response("Bad request"),
        },
        tags=[tags]
    )
    def get(self, request):
        try:
            subscriptions = Subscription.objects.filter(client=request.user, status="active").first()  # first
            if subscriptions:
                serializer = SubscriptionSerializer(subscriptions)
                return Response(serializer.data, status=200)
            return Response("You have no subscription", status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Annuler un abonnement",
        responses={
            200: openapi.Response("Subscription canceled", SubscriptionSerializer),
            400: openapi.Response("This subscription is expired or already cancelled"),
            500: openapi.Response("Internal Server error")
        },
        tags=[tags]
    )
    def patch(self, request, pk):
        try:
            subscription = get_object(request, pk)
            if subscription.status in ["cancelled", "expired"]:
                return Response("This subscription is expired or already cancelled", status=status.HTTP_400_BAD_REQUEST)

            else:
                subscription.status = "cancelled"
                subscription.save()
                return Response({"message": "Subscription cancelled successfully"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RenewSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Renouveller un abonnement",
        responses={
            200: openapi.Response("Subscription renewed successfully", SubscriptionSerializer),
            400: openapi.Response("Subscription cannot be renewed"),
            500: openapi.Response("Internal Server Error")
        },
        tags=[tags]
    )
    def post(self, request, pk):
        subscription = get_object(request, pk)
        if subscription.status == "expired":
            subscription.start_date = datetime.now().date()
            subscription.end_date = datetime.now().date() + relativedelta(months=subscription.sub_plan.duration_month)
            subscription.status = "active"
            subscription.save()
            return Response({"message": "Subscription renewed successfully"}, status=200)
        return Response({"error": "Subscription cannot be renewed"}, status=400)
