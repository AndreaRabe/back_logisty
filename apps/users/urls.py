from django.urls import path

from apps.users import views_admin, views_individual_client, views_client_company, views_driver, \
    views_driverChef_request, views_chief_fleet

user_urlpatterns = [
    # For admin
    path("admin_signup/", views_admin.AdminView.as_view(), name='Singup Admin'),
    path("admin_profile/", views_admin.AdminProfileView.as_view(), name='Profile Admin'),
    path("admins_list/", views_admin.AdminGetView.as_view(), name='Admins List'),

    # For Client Company
    path("client_company_signup/", views_client_company.ClientCompanyView.as_view(), name='Client Company signup'),
    path("client_company_profile/", views_client_company.ClientCompanyProfileView.as_view(),
         name='Client Company profile'),
    path("clients_company_list/", views_client_company.ClientCompanyGetView.as_view(), name="Client company list"),

    # For Driver
    path("driver_signup/", views_driver.DriverView.as_view(), name='Driver signup'),
    path("driver_profile/", views_driver.DriverProfileView.as_view(), name='Driver profile'),
    path("drivers_list/", views_driver.DriverGetView.as_view(), name="Driver list"),

    # For Client
    path("client_signup/", views_individual_client.ClientParticulierView.as_view(), name='Signup Client'),
    path("client_profile/", views_individual_client.ClientParticulierProfileView.as_view(), name='Profile Client'),
    path("clients_list/", views_individual_client.ClientParticulierGetView.as_view(), name='List Client'),

    # For Chief Fleet
    path("chief_fleet_signup/", views_chief_fleet.ChiefFleetView.as_view(), name='signup Chief Fleet'),
    path("chief_fleet_profile/", views_chief_fleet.ChiefFleetProfileView.as_view(), name="Profile Chief Fleet"),
    path("chief_fleet_list/", views_chief_fleet.ChiefFleetGetView.as_view(), name="Chief list"),

    # For Driver request for chief fleet
    path("driver_request_signup/", views_driverChef_request.DriverChiefRequestView.as_view(), name="create request"),
    path("driver_request_detail/<int:pk>", views_driverChef_request.DriverChiefRequestDetailView.as_view(),
         name="detail for request"),
    path("drivers_list/", views_driver.DriverGetView.as_view(), name='List Drivers'),
]
