import os
import string
import subprocess

import ffmpeg
from celery import shared_task
from django.conf import settings
from faster_whisper import WhisperModel

from .models import VideoJob
from .helpers import transcribe_with_timestamps


@shared_task
def censor_video(video_id):
    videojob = VideoJob.objects.get(id=video_id)
    input_path = videojob.input_video.path
    output_path = videojob.get_output_video_path()
    output_dir = os.path.dirname(output_path)
    # Create a dir branch for processed videos if not present
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    word_timings = transcribe_with_timestamps(input_path, "ru")
    bad_words = {"программисты", "инженеры", "линукс"}

    target_timestamps = []
    for w in bad_words:
        if w in word_timings:
            target_timestamps += word_timings[w]

    video = ffmpeg.input(input_path)
    muted_audio = video.audio
    for start, end in target_timestamps:
        muted_audio = muted_audio.filter(
            "volume",
            enable=f"between(t,{start - 0.05},{end + 0.12})",
            volume=0,
        )

    output = ffmpeg.output(video.video, muted_audio, output_path)
    ffmpeg.run(output)

    relative_output_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
    videojob.output_video = relative_output_path
    videojob.size = round(os.path.getsize(output_path) / (2**20), 2)
    videojob.status = videojob.COMPLETED
    videojob.save()

    return "CELERY TASK DONE!!!"
