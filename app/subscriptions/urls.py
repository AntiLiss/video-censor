from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from .views import SubscriptionViewSet

app_name = "subscriptions"

router = DefaultRouter()
# router.register("", SubscriptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
