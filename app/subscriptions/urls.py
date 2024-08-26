from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (PaymentCreateView, SubPlanReadViewSet, SubscriptionViewSet,
                    YookassaWebhookView)

app_name = "subscriptions"

router = DefaultRouter()
router.register("sub-plans", SubPlanReadViewSet)
router.register("subscriptions", SubscriptionViewSet)

urlpatterns = [
    path(
        "subscriptions/<int:subscription_pk>/create-payment/",
        PaymentCreateView.as_view(),
        name="create-payment",
    ),
    path(
        "subscriptions/yookassa-webhooks/",
        YookassaWebhookView.as_view(),
        name="yookassa-webhooks",
    ),
    path("", include(router.urls)),
]
