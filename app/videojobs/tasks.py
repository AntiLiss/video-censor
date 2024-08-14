import os
import string
import subprocess

import ffmpeg
from celery import shared_task
from django.conf import settings
from faster_whisper import WhisperModel

from .models import VideoJob


def whisper_transcribe(whisper_model, file_path, lang):
    """
    Trancribe audio using whisper model and return word object list with
    timestamps
    """
    segments, _ = whisper_model.transcribe(
        file_path,
        language=lang,
        word_timestamps=True,
    )
    word_objects = []

    for segment in segments:
        for word in segment.words:
            word_objects.append(word)

    return word_objects


@shared_task
def censor_video(video_id):
    videojob = VideoJob.objects.select_related(
        "audio_setting",
        "video_setting",
    ).get(id=video_id)

    input_path = videojob.input_video.path
    output_path = videojob.get_output_video_path()
    output_dir = os.path.dirname(output_path)

    # Create directory path for processed videos if not present
    os.makedirs(output_dir, exist_ok=True)

    # Transcribe a file
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    word_objects = whisper_transcribe(model, input_path, videojob.language)

    bad_words = {"62"}
    video = ffmpeg.input(input_path)
    muted_audio = video.audio

    for obj in word_objects:
        # Normalize the word
        word = (
            obj.word.translate(str.maketrans("", "", string.punctuation))
            .lower()
            .strip()
        )

        # Mute the word if it's in set
        if word in bad_words:
            # Expand the time frame to make sure the word is included
            end = obj.end + 0.15
            muted_audio = muted_audio.filter(
                "volume",
                enable=f"between(t,{obj.start},{end})",
                volume=0,
            )

    output = ffmpeg.output(video.video, muted_audio, output_path)
    ffmpeg.run(output)

    relative_output_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
    videojob.output_video = relative_output_path
    videojob.size = round(os.path.getsize(output_path) / (2**20), 2)
    videojob.status = videojob.COMPLETED
    videojob.save()
    print(videojob.audio_setting.get_own_word_set())

    return "CELERY TASK DONE!!!"
