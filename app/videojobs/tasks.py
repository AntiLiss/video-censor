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
    Trancribe video using whisper model and return a list of word info
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
            # Merge word parts separated by the `-` into 1 word, cuz whisper
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
        return {line.strip().lower() for line in f if line.strip()}


def collect_ban_words(audio_setting, videojob):
    """Collect ban words from own_words and corresponding file"""
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

    return ban_words


def mute_words(input, output, ban_words, lang):
    """Mute provided words in video and save the video in output_path"""
    # Transcribe a file
    model = WhisperModelSingleton("medium", device="cpu", compute_type="int8")
    words = whisper_transcribe(model, input, lang)

    # Collect audio filter commands
    audio_filters = [
        f"volume=enable='between(t,{w['start']},{w['end'] + 0.1})':volume=0"
        for w in words
        if w["value"] in ban_words
    ]
    filter_chain = ",".join(audio_filters)

    if filter_chain:
        ffmpeg.input(input).output(
            output,
            af=filter_chain,
            vcodec="copy",
            acodec="aac",
        ).run()
    else:
        ffmpeg.input(input).output(
            output,
            vcodec="copy",
            acodec="copy",
        ).run()


def complete_videjob(videojob, error_msg=None):
    """Complete VideoJob instance fields"""
    output_path = videojob.get_output_video_path()

    if not error_msg:
        videojob.status = videojob.COMPLETED
        videojob.output_video = os.path.relpath(
            output_path,
            settings.MEDIA_ROOT,
        )
        videojob.size = round(os.path.getsize(output_path) / (2**20), 2)
    else:
        videojob.status = videojob.FAILED
        videojob.error_message = error_msg

    videojob.save()


@shared_task
def censor_video(video_id):
    """Mute ban words in video"""
    videojob = VideoJob.objects.select_related(
        "audio_setting",
        "video_setting",
    ).get(id=video_id)

    input_path = videojob.input_video.path
    output_path = videojob.get_output_video_path()
    # Create directory for processed videos if not present
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    audio_setting = videojob.audio_setting

    if not audio_setting or not audio_setting.is_applied():
        ffmpeg.input(input_path).output(
            output_path,
            vcodec="copy",
            acodec="copy",
        ).run()
        return complete_videjob(videojob)

    try:
        ban_words = collect_ban_words(audio_setting, videojob)
        if not ban_words:
            return complete_videjob(videojob, "Can't collect ban words")

        if not has_audio(input_path):
            return complete_videjob(
                videojob, "The video has no audio to apply sound censorship"
            )

        mute_words(input_path, output_path, ban_words, videojob.language)
        complete_videjob(videojob)
    except Exception as e:
        print(str(e))
        complete_videjob(videojob, "Unexpected error")
