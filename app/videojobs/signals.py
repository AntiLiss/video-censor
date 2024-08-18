from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import VideoJob


@receiver(post_delete, sender=VideoJob)
def delete_video_files(sender, instance, **kwargs):
    """Delete video files corresponding to videojob"""
    instance.input_video.delete(save=False)
    if instance.output_video:
        instance.output_video.delete(save=False)
