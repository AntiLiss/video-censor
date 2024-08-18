import os
import re
from functools import lru_cache

import ffmpeg
from celery import shared_task
from django.conf import settings
from faster_whisper import WhisperModel

from .models import VideoJob
from .utils import Singleton, has_audio


class Transcriber(
    WhisperModel,
    metaclass=Singleton,  # Singleton cuz WhisperModel init takes a time
):
    """Transcribe video/audio using whisper model"""

    def transcribe_with_timestamps(self, file_path, lang):
        """
        Transcribe to a list of word info dictionaries with timestamps
        included
        """
        segments, _ = super().transcribe(
            file_path,
            language=lang,
            word_timestamps=True,
        )
        words = []

        for segment in segments:
            for w in segment.words:
                # Merge hypenated words into 1 word, as whisper may split
                # word like `check-in` into `check` and `-in`.
                # NOTE: First word can't start with hyphen unless whisper
                # makes a mistake
                if w.word.startswith("-"):
                    words[-1]["value"] += w.word
                    continue

                word_info = {
                    "value": self.__normalize_word(w.word),
                    "start": w.start,
                    "end": w.end,
                }
                words.append(word_info)

        return words

    def __normalize_word(self, word):
        """Bring the word to the valid format"""
        return re.sub(r"[^\w -]", "", word.lower().strip())


class VideoSpeechCensor:
    """Remove unwanted words from a video"""

    def censor(self, input, output, ban_words, lang):
        # Transcribe input video
        model = Transcriber("medium", device="cpu", compute_type="int8")
        words = model.transcribe_with_timestamps(input, lang)

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


def collect_ban_words(audio_setting, videojob):
    """Collect ban words from own_words and corresponding file"""
    ban_words = audio_setting.get_own_word_set()

    @lru_cache(maxsize=None)
    def pull_words_from_file(filename):
        """Read file and return set of words"""
        with open(filename, "r", encoding="utf8") as f:
            return {line.strip().lower() for line in f if line.strip()}

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
    return error_msg or "Processing completed"


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
        if not has_audio(input_path):
            return complete_videjob(
                videojob, "The video has no audio to apply sound censorship"
            )

        ban_words = collect_ban_words(audio_setting, videojob)
        if not ban_words:
            return complete_videjob(videojob, "Can't collect ban words")

        VideoSpeechCensor().censor(
            input_path,
            output_path,
            ban_words,
            videojob.language,
        )
        return complete_videjob(videojob)
    except Exception as e:
        print(str(e))
        return complete_videjob(videojob, "Unexpected error")
