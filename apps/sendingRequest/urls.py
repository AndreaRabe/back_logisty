from django.urls import path

from apps.sendingRequest.views import SendingRequestView, SendingRequestDetailsView, AdminSendingRequestDetailsView, \
    AdminSendingRequestUpdateView

sending_request_urlpatterns = [
    path("sending_request/", SendingRequestView.as_view(), name="sending_request"),
    path("sending_request_details/<int:pk>", SendingRequestDetailsView.as_view(), name="sending_request_details"),
    path("send_request_details_admin/", AdminSendingRequestDetailsView.as_view(),
         name="send_request_details_admin"),
    path("send_request_update_admin/<int:pk>", AdminSendingRequestUpdateView.as_view(),
         name="send_request_update_admin"),
]
