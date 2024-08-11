import os
import subprocess

from celery import shared_task
from django.conf import settings

from .models import VideoJob


@shared_task
def reverse_video(video_id):
    videojob = VideoJob.objects.get(id=video_id)

    input_path = videojob.input_video.path
    output_path = videojob.get_output_video_path()
    output_dir = os.path.dirname(output_path)
    # Create a dir branch for processed videos if not present
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    command = f"ffmpeg -i {input_path} -vf reverse -af areverse {output_path}"
    subprocess.run(command, shell=True, check=True)

    relative_output_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
    videojob.output_video = relative_output_path
    videojob.size = round(os.path.getsize(output_path) / (2**20), 2)
    videojob.status = videojob.COMPLETED
    videojob.save()

    return "MY RESULT!!!"
