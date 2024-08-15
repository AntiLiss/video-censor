import os
import re
import string

import ffmpeg
from celery import shared_task
from django.conf import settings
from faster_whisper import WhisperModel

from .models import VideoJob


def whisper_transcribe(whisper_model, file_path, lang):
    """
    Trancribe audio using whisper model and return list of word info
    dictionaries with timestamps
    """
    segments, _ = whisper_model.transcribe(
        file_path,
        language=lang,
        word_timestamps=True,
    )
    words = []

    for segment in segments:
        for word in segment.words:
            word_info = {
                "value": word.word,
                "start": word.start,
                "end": word.end,
            }
            # Unite word parts separated by the `-` into 1 word, cuz whisper
            # thinks that word like `check-in` is 2 words: `check` and `-in`
            # TODO: It may break if transcribed incorrectly. Improve!
            if word_info["value"].startswith("-"):
                words[-1]["value"] += word_info["value"]
                continue

            words.append(word_info)

    return words


@shared_task
def censor_video(video_id):
    """Mute restricted words in video"""
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
    words = whisper_transcribe(model, input_path, videojob.language)

    # Prepare a set with all restricted words
    bad_words = videojob.audio_setting.get_own_word_set()

    # if videojob.audio_setting.profanity:
    #     with open(f"profanity_{videojob.language}.txt", "r", encoding="utf8") as f:
    #         for word in f:
    #             bad_words.add(word.lower().strip())

    # if videojob.audio_setting.xenophobia:
    #     with open(f"xenophobia_{videojob.language}.txt", "r", encoding="utf8") as f:
    #         for word in f:
    #             bad_words.add(word.lower().strip())

    video = ffmpeg.input(input_path)
    muted_audio = video.audio

    for w in words:
        if not bad_words:
            break
        # Normalize the word
        word = re.sub(r"[^\w -]", "", w["value"].lower().strip())
        # Mute the word if it's in set
        if word in bad_words:
            # Expand the time frame to make sure the word is included
            end = w["end"] + 0.1
            muted_audio = muted_audio.filter(
                "volume",
                enable=f"between(t,{w['start']},{end})",
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
