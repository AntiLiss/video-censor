import os
import re
from functools import lru_cache

import ffmpeg
from celery import shared_task
from django.conf import settings

from .models import VideoJob
from .utils import WhisperModelSingleton, has_audio


def whisper_transcribe(whisper_model, file_path, lang):
    """
    Trancribe audio using whisper model and return list of word info
    dictionaries with timestamps
    """
    segments, _ = whisper_model.transcribe(
        file_path, language=lang, word_timestamps=True
    )
    words = []

    for segment in segments:
        for w in segment.words:
            word_info = {
                # Normalize the word value
                "value": re.sub(r"[^\w -]", "", w.word.lower().strip()),
                "start": w.start,
                "end": w.end,
            }
            # Unite word parts separated by the `-` into 1 word, cuz whisper
            # thinks that word like `check-in` is 2 words: `check` and `-in`
            if word_info["value"].startswith("-"):
                words[-1]["value"] += word_info["value"]
                continue
            words.append(word_info)

    return words


@lru_cache(maxsize=None)
def pull_words_from_file(filename):
    """Read file and return set of words"""
    with open(filename, "r", encoding="utf8") as f:
        words = {line.strip().lower() for line in f if line.strip()}
    return words


@shared_task
def censor_video(video_id):
    """Mute ban words in video"""
    videojob = VideoJob.objects.select_related(
        "audio_setting",
        "video_setting",
    ).get(id=video_id)

    audio_setting = videojob.audio_setting

    if not audio_setting or not audio_setting.is_configured():
        return "NO AUDIO SETTING"

    input_path = videojob.input_video.path
    output_path = videojob.get_output_video_path()
    # Create directory for processed videos if not present
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Collect all ban words into a set
    ban_words = audio_setting.get_own_word_set()

    if audio_setting.profanity:
        profanity_file = os.path.join(
            settings.BAN_WORDS_DIR,
            f"profanity_{videojob.language}.txt",
        )
        ban_words.update(pull_words_from_file(profanity_file))

    if audio_setting.insult:
        insult_file = os.path.join(
            settings.BAN_WORDS_DIR,
            f"insult_{videojob.language}.txt",
        )
        ban_words.update(pull_words_from_file(insult_file))

    # Abort processing if no ban words are provided
    if not ban_words:
        return "No ban word found"

    # Ensure video has audio
    if not has_audio(input_path):
        videojob.status = videojob.FAILED
        videojob.error_message = "Video has no audio!"
        videojob.save()
        return videojob.error_message

    # Transcribe a file
    model = WhisperModelSingleton("medium", device="cpu", compute_type="int8")
    words = whisper_transcribe(model, input_path, videojob.language)

    # Collect audio filter commands
    audio_filters = [
        f"volume=enable='between(t,{w['start']},{w['end'] + 0.1})':volume=0"
        for w in words
        if w["value"] in ban_words
    ]
    # for w in words:
    #     if w["value"] in ban_words:
    #         # Expand the time frame to ensure coverage
    #         end = w["end"] + 0.1
    #         audio_filters.append(
    #             f"volume=enable='between(t,{w['start']},{end})':volume=0"
    #         )

    if audio_filters:
        complex_filter = ",".join(audio_filters)
        ffmpeg.input(input_path).output(
            output_path,
            af=complex_filter,
            vcodec="copy",
            acodec="aac",
            strict="experimental",
        ).run()
    else:
        ffmpeg.input(input_path).output(output_path).run()

    relative_output_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
    videojob.output_video = relative_output_path
    videojob.size = round(os.path.getsize(output_path) / (2**20), 2)
    videojob.status = videojob.COMPLETED
    videojob.save()

    return "CELERY TASK DONE!!!"
