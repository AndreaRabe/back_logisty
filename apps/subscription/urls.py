from django.urls import path

from apps.subscription.view_subscription import SubscriptionView, CancelSubscriptionView, RenewSubscriptionView
from apps.subscription.views_subscription_plan import SubscriptionPlanView, SubscriptionPlanListView, \
    SubscriptionPlanDetailsView

subscription_plan_urlpatterns = [
    # subscription plan
    path("subscription_plan/", SubscriptionPlanView.as_view(), name="create_subscription_plan"),
    path("subscription_plan/list/", SubscriptionPlanListView.as_view(), name="list_subscription_plan"),
    path("subscription_plan/details/<int:pk>", SubscriptionPlanDetailsView.as_view(), name="details_subscription_plan"),

    # subscription
    path("subscription/", SubscriptionView.as_view(), name="create_subscription"),
    path("subscription/cancel/<int:pk>", CancelSubscriptionView.as_view(), name="cancel_subscription"),
    path("subscription/renew/<int:pk>", RenewSubscriptionView.as_view(), name="renew_subscription"),

]
