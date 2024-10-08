from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import VideojobViewSet

app_name = "videojobs"

router = DefaultRouter()
router.register("", VideojobViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
