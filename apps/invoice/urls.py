from django.urls import path

from apps.invoice.views import SubscriptionInvoiceView, SendingRequestInvoiceView

invoice_urlpatterns = [
    path("invoice/subscription/<int:pk>", SubscriptionInvoiceView.as_view(), name="Invoice for subscription"),
    path("invoice/sending_request/<int:pk>", SendingRequestInvoiceView.as_view(), name="Invoice for sending request")
]
