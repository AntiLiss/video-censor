from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PaymentCreateView, SubPlanReadViewSet, SubscriptionViewSet

app_name = "subscriptions"

router = DefaultRouter()
router.register("sub-plans", SubPlanReadViewSet)
router.register("subscriptions", SubscriptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "subscriptions/<int:subscription_pk>/create-payment/",
        PaymentCreateView.as_view(),
        name="create-payment",
    ),
]
