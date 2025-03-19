from io import BytesIO

from django.http import Http404, FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.invoice.models import SubscriptionInvoice, SendingRequestInvoice
from apps.invoice.serializers import SubscriptionInvoiceSerializer, SendingRequestInvoiceSerializer
from apps.sendingRequest.serializers import SendingRequestSerializer
from apps.subscription.models import SubscriptionPlan, Subscription
from apps.subscription.serializers import SubscriptionPlanSerializer, SubscriptionSerializer


def invoice_sending_request_post(request):
    data = {
        "client": request["client"],
        "sending_request": request["id"],
        "total_ttc": None,
    }
    serializer = SendingRequestInvoiceSerializer(data=data)
    if serializer.is_valid():
        serializer.save()


def subscription_request_post(request, price):
    data = {
        "client": request["client"],
        "sub_plan": request["sub_plan"],
        "total_ttc": price,
    }
    serializer = SubscriptionInvoiceSerializer(data=data)
    if serializer.is_valid():
        serializer.save()


def get_subscription_invoices(request, pk):
    try:
        return SubscriptionInvoice.objects.get(pk=pk, client=request.user)
    except SubscriptionInvoice.DoesNotExist:
        raise Http404("Subscription not found")


def get_sending_request_invoice(request, pk):
    try:
        return SendingRequestInvoice.objects.get(pk=pk, client=request.user)
    except SendingRequestInvoice.DoesNotExist:
        raise Http404("Invoice not found")


tags = "Generate Invoice"


class SubscriptionInvoiceView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Creer un facture pour la subscription",
        responses={
            200: openapi.Response("Invoice pdf"),
            400: openapi.Response("Bad Request")
        },
        tags=[tags]
    )
    def post(self, request, pk):
        invoice = get_subscription_invoices(request, pk)
        serializer = SubscriptionInvoiceSerializer(invoice)
        invoice_data = serializer.data

        # Génération du PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 50, "FACTURE D'ABONNEMENT")

        # Invoice Details
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 100, f"Numéro de facture: {invoice_data['invoice_number']}")
        p.drawString(50, height - 120, f"Date de création: {invoice_data['created_at'][:10]}")

        # Client Details
        client = invoice_data['client_details']
        p.drawString(50, height - 160, "Informations du client:")
        p.drawString(70, height - 180, f"Nom: {client['first_name']} {client['last_name']}")
        p.drawString(70, height - 200, f"Email: {client['email']}")
        p.drawString(70, height - 220, f"Téléphone: {client['phone']}")
        p.drawString(70, height - 240, f"Adresse: {client['address']}")

        # Subscription Plan Details
        sub_plan = invoice_data['sub_plan_details']
        subscription = SubscriptionSerializer(Subscription.objects.get(client=request.user, status="active"))
        sub_plan_data = SubscriptionPlanSerializer(SubscriptionPlan.objects.get(pk=sub_plan['sub_plan']))

        sub_name = sub_plan_data.data["name"]
        p.drawString(50, height - 280, "Détails de l'abonnement:")
        p.drawString(70, height - 300, f"Nom du plan: {sub_name}")
        p.drawString(70, height - 320, f"Date de début: {subscription.data['start_date']}")
        p.drawString(70, height - 340, f"Date de fin: {subscription.data['end_date']}")
        p.drawString(70, height - 360, f"Statut: {subscription.data['status']}")

        # Payment Details
        p.drawString(50, height - 400, "Informations de paiement:")
        p.drawString(70, height - 420, f"Montant total: {invoice_data['total_ttc']} Ar")
        p.drawString(70, height - 440, f"Méthode de paiement: {invoice_data['payment_method']}")
        p.drawString(70, height - 460, f"Statut de paiement: {invoice_data['status']}")

        # Save the PDF
        p.showPage()
        p.save()
        buffer.seek(0)

        # Retourner le fichier PDF en réponse
        response = FileResponse(buffer, as_attachment=True,
                                filename=f"invoice_{invoice_data['invoice_number']}_{client['username']}.pdf")

        return response


class SendingRequestInvoiceView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Créer une facture pour la demande d'envoi",
        responses={
            200: openapi.Response("Invoice pdf"),
            400: openapi.Response("Bad Request")
        },
        tags=[tags]
    )
    def post(self, request, pk):
        invoice = get_sending_request_invoice(request, pk)
        invoice_serializer = SendingRequestInvoiceSerializer(invoice)
        invoice_data = invoice_serializer.data

        sending_request = invoice.sending_request
        sending_request_serializer = SendingRequestSerializer(sending_request)
        sending_request_data = sending_request_serializer.data

        # Génération du PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Titre de la facture
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 50, "FACTURE DE DEMANDE D'ENVOI")

        # Détails de la facture
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 100, f"Numéro de facture: {invoice_data['invoice_number']}")
        p.drawString(50, height - 120, f"Date de création: {invoice_data['created_at'][:10]}")

        # Informations du client
        client = invoice_data['client_details']
        p.drawString(50, height - 160, "Informations du client:")
        p.drawString(70, height - 180, f"Nom: {client['first_name']} {client['last_name']}")
        p.drawString(70, height - 200, f"Email: {client['email']}")
        p.drawString(70, height - 220, f"Téléphone: {client['phone']}")
        p.drawString(70, height - 240, f"Adresse: {client['address']}")

        # Détails de la demande d'envoi
        p.drawString(50, height - 280, "Détails de l'envoi:")
        p.drawString(70, height - 300, f"Destinataire: {sending_request_data['recipient_name']}")
        p.drawString(70, height - 320, f"Téléphone: {sending_request_data['recipient_phone']}")
        p.drawString(70, height - 340, f"Email: {sending_request_data['recipient_email']}")
        p.drawString(70, height - 360, f"Type de colis: {sending_request_data['cargo_type']}")
        p.drawString(70, height - 380, f"Poids: {sending_request_data['weight']} kg")
        p.drawString(70, height - 400, f"Quantité: {sending_request_data['quantity']}")
        p.drawString(70, height - 420, f"Lieu de prise en charge: {sending_request_data['pickup_location']}")
        p.drawString(70, height - 440, f"Date de prise en charge: {sending_request_data['pickup_date_time']}")
        p.drawString(70, height - 460, f"Lieu de livraison: {sending_request_data['delivery_location']}")
        p.drawString(70, height - 480, f"Date de livraison: {sending_request_data['delivery_date_time']}")
        p.drawString(70, height - 500, f"Priorité: {sending_request_data['priority']}")

        # Informations de paiement
        p.drawString(50, height - 540, "Informations de paiement:")
        p.drawString(70, height - 560, f"Montant total: {invoice_data['total_price']} Ar")
        p.drawString(70, height - 600, f"Statut de paiement: {invoice_data['status']}")

        # Sauvegarde du PDF
        p.showPage()
        p.save()
        buffer.seek(0)

        # Retourner le fichier PDF en réponse
        response = FileResponse(buffer, as_attachment=True,
                                filename=f"sending_request_invoice_{invoice_data['invoice_number']}_{client['username']}.pdf")
        return response
