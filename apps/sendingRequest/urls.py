from django.urls import path

from apps.sendingRequest.views import SendingRequestView, SendingRequestDetailsView, AdminSendingRequestDetailsView, \
    AdminSendingRequestUpdateView, ChiefFleetSendingRequestDetailsView
from apps.sendingRequest.views_fleet_assignment import FleetAssignmentView, FleetAssignmentDetailsView

sending_request_urlpatterns = [
    # Sending Request
    path("sending_request/", SendingRequestView.as_view(), name="sending_request"),
    path("sending_request_details/<int:pk>", SendingRequestDetailsView.as_view(), name="sending_request_details"),
    path("sending_request_details_admin/", AdminSendingRequestDetailsView.as_view(),
         name="send_request_details_admin"),
    path("sending_request_update_admin/<int:pk>", AdminSendingRequestUpdateView.as_view(),
         name="send_request_update_admin"),
    path("sending_request_details_chief/", ChiefFleetSendingRequestDetailsView.as_view(),
         name="List of request for Chief"),

    # Sending Request Assignment
    path("sending_request_assignment/", FleetAssignmentView.as_view(), name="Assignment_request"),
    path("sending_request_assignment_details/<int:pk>", FleetAssignmentDetailsView.as_view(),
         name="Assignment_request_details"),
]
