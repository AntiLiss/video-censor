from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .models import VideoJob
from .serializers import VideoJobCreateSerializer, VideoJobReadSerializer
# from .tasks import reverse_video


class VideojobViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    "Create, Read, Destroy videojobs"

    permission_classes = [IsAuthenticated]
    queryset = VideoJob.objects.all()
    serializer_class = VideoJobReadSerializer

    def get_serializer_class(self):
        # Switch serializer when create action
        if self.action == "create":
            return VideoJobCreateSerializer
        return self.serializer_class

    def get_queryset(self):
        # Limit videojobs to this user
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Set this user to user field
        videojob = serializer.save(user=self.request.user)
        # reverse_video.delay_on_commit(videojob.id)
