import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import VideoJob


@receiver(post_delete, sender=VideoJob)
def delete_video_files(sender, instance, **kwargs):
    """Delete video files corresponding to videojob"""
    input = instance.input_video
    output = instance.output_video

    if input and os.path.isfile(input.path):
        os.remove(input.path)
    if output and os.path.isfile(output.path):
        os.remove(output.path)
