"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from apps.core.drf_yasg_config import swagger_urlpatterns
from apps.invoice.urls import invoice_urlpatterns
from apps.sendingRequest.urls import sending_request_urlpatterns
from apps.subscription.urls import subscription_plan_urlpatterns
from apps.truck.urls import truck_urlpatterns
from apps.users.urls import user_urlpatterns

urlpatterns = [
    # Auth
    path("auth/", include('djoser.urls')),
    path("auth/", include('djoser.urls.jwt')),
    # path("auth/", include('djoser.urls.authtoken')),  # Generer autom dans djoser

    path('admin/', admin.site.urls),
    path('api/v1/', include(user_urlpatterns)),
    path('api/v1/', include(sending_request_urlpatterns)),
    path('api/v1/', include(subscription_plan_urlpatterns)),
    path('api/v1/', include(invoice_urlpatterns)),
    path('api/v1/', include(truck_urlpatterns))
]

urlpatterns.extend(swagger_urlpatterns)
