from django.urls import path

from apps.truck.views import TruckView, TruckDetail, TruckListView

truck_urlpatterns = [
    path('truck/add/', TruckView.as_view(), name='Add new truck'),
    path('truck/details/<int:pk>', TruckDetail.as_view(), name="Truck details"),
    path('truck/list/', TruckListView.as_view(), name="Truck list")
]
