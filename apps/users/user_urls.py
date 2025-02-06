from django.urls import path

from apps.users import views_admin, views_individual_client, views_client_company, views_driver

user_urlpatterns = [
    # For admin
    path("admin_signup/", views_admin.AdminView.as_view(), name='Singup Admin'),
    path("admin_profile/", views_admin.AdminProfileView.as_view(), name='Profile Admin'),

    # For Client Company
    path("client_company_signup/", views_client_company.ClientCompanyView.as_view(), name='Client Company signup'),
    path("client_company_profile/", views_client_company.ClientCompanyProfileView.as_view(),
         name='Client Company profile'),

    # For Driver
    path("driver_signup/", views_driver.DriverView.as_view(), name='Driver signup'),
    path("driver_profile/", views_driver.DriverProfileView.as_view(), name='Driver profile'),

    # For Client
    path("client_signup/", views_individual_client.ClientParticulierView.as_view(), name='Signup Client'),
    path("client_profile/", views_individual_client.ClientParticulierProfileView.as_view(), name='Profile Client'),
]
