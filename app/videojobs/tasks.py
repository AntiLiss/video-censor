import os
import re
import subprocess
from functools import lru_cache
from uuid import uuid4
import shutil
from celery import shared_task
from django.conf import settings
from faster_whisper import WhisperModel
from pydub import AudioSegment
from pydub.generators import Sine
from django.core.files import File
from .models import VideoJob
from .utils import Singleton, UserOutputError, has_audio


class Transcriber(
    WhisperModel,
    metaclass=Singleton,  # Singleton cuz WhisperModel init takes long time
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
                    words[-1]["value"] += self.__normalize_word(w.word)
                    continue
                words.append(
                    {
                        "value": self.__normalize_word(w.word),
                        "start": w.start,
                        "end": w.end,
                    }
                )
        return words

    def __normalize_word(self, word):
        """Bring the word to the valid format"""
        return re.sub(r"[^\w -]", "", word.lower().strip())


class VideoSoundCensor:
    """Censor unwanted words in video"""

    def censor(self, input, ban_words, lang):
        """Censor video's audio and return modified audio path"""
        self.__raise_no_sound_error(input)
        self.__raise_no_ban_words_error(ban_words)

        # Transcribe input file
        model = Transcriber("medium", device="cpu", compute_type="int8")
        words = model.transcribe_with_timestamps(input, lang)
        # Extract audio
        audio = AudioSegment.from_file(input)

        # Apply censoring sound to detected ban words
        for w in words:
            if w["value"] in ban_words:
                start_ms, end_ms = w["start"] * 1000, w["end"] * 1000
                duration_ms = end_ms - start_ms
                beep_sound = self.__create_beep_sound(duration_ms)
                audio = audio[:start_ms] + beep_sound + audio[end_ms:]

        # Save censored audio as temporary file
        censored_audio_path = os.path.join(
            settings.TEMP_FILES_DIR,
            f"{uuid4()}.wav",
        )
        audio.export(censored_audio_path, format="wav")
        return censored_audio_path

    def __raise_no_sound_error(self, video_path):
        """Raise error if video has no sound"""
        if not has_audio(video_path):
            raise UserOutputError(
                "The video has no audio to apply sound censorship",
            )

    def __raise_no_ban_words_error(self, ban_words):
        """Raise error if no ban words"""
        if not ban_words:
            raise ValueError("Can't collect ban words")

    def __create_beep_sound(self, duration_ms):
        """Create beep sound object"""
        beep = Sine(1000).to_audio_segment(duration=duration_ms)
        return beep - 20  # Reduce volume


class VideoPictureCensor:
    def censor(self):
        return


class CensorshipProcessor:
    """Censor visual and audio parts of video"""

    def __init__(self, videojob):
        self.videojob = videojob

        self.input_video_path = videojob.input_video.path
        self.output_video_path = videojob.get_output_video_path()

        self.audio_setting = videojob.audio_setting
        self.video_setting = videojob.video_setting

    def run(self):
        """
        Apply visual and audio censorship and save result video to output
        path of videojob
        """
        # If no settings are specified save as is
        if not self.__has_audio_setting() and not self.__has_video_setting():
            return self.__save_video_as_is()

        censured_audio = None
        censured_picture = None

        # Apply audio censorship if requested
        if self.__has_audio_setting():
            ban_words = self.__collect_ban_words()
            censured_audio = VideoSoundCensor().censor(
                self.input_video_path,
                ban_words,
                self.videojob.language,
            )

        # Apply visual censorship if requested
        if self.__has_video_setting():
            censured_picture = VideoPictureCensor().censor()

        # Save the rusult to output path
        self.__save_censored_video(
            censured_picture,
            censured_audio,
            has_audio(self.input_video_path),
        )

        # Clean up indermediate files
        # if os.path.isfile(censured_audio or ""):
        #     os.remove(censured_audio)
        # if os.path.isfile(censured_picture or ""):
        #     os.remove(censured_picture)
        # os.remove

        # TODO: Docker raises PermissionDenied error. Fix
        shutil.rmtree(settings.TEMP_FILES_DIR)
        os.makedirs(settings.TEMP_FILES_DIR, exist_ok=True)

        return None

    def __has_audio_setting(self):
        return self.audio_setting and self.audio_setting.is_applied()

    def __has_video_setting(self):
        return self.video_setting and self.video_setting.is_applied()

    def __collect_ban_words(self):
        """Collect ban words from own_words and corresponding files"""
        ban_words = self.audio_setting.get_own_word_set()

        @lru_cache(maxsize=None)
        def pull_words_from_file(filename):
            """Read file and return set of words"""
            with open(filename, "r", encoding="utf8") as f:
                return {line.strip().lower() for line in f if line.strip()}

        # Add ban words from predefined files
        if self.audio_setting.profanity:
            profanity_file = os.path.join(
                settings.BAN_WORDS_DIR,
                f"profanity_{self.videojob.language}.txt",
            )
            ban_words.update(pull_words_from_file(profanity_file))

        if self.audio_setting.insult:
            insult_file = os.path.join(
                settings.BAN_WORDS_DIR,
                f"insult_{self.videojob.language}.txt",
            )
            ban_words.update(pull_words_from_file(insult_file))

        return ban_words

    def __save_video_as_is(self):
        """Save input video as is"""
        # fmt: off
        command = [
            'ffmpeg',
            '-i', self.input_video_path,
            '-c:v', 'copy',
            '-c:a', 'copy',
            self.output_video_path,
        ]
        # fmt: on
        subprocess.run(command)

    def __save_censored_video(self, censured_video, censured_audio, has_audio=True):
        """Save censored video and audio to one output file"""
        # Merge censored parts if present
        # fmt: off
        command = [
            "ffmpeg",
            "-i", censured_video or self.input_video_path,
            "-i", censured_audio or self.input_video_path,
            "-c:v", 'libx264' if censured_video else "copy",
            "-c:a", "aac" if censured_audio else 'copy',
            "-map", "0:v:0",
            *(["-map", "1:a:0"] if has_audio else []),
            self.output_video_path,
        ]
        # fmt: on
        subprocess.run(command)


def complete_videojob(videojob, error_msg=None):
    """Update videojob fields and save instance"""
    if error_msg:
        videojob.status = videojob.FAILED
        videojob.error_message = error_msg
    else:
        videojob.status = videojob.COMPLETED
        output_video_path = videojob.get_output_video_path()
        # videojob.output_video.path = os.path.relpath(
        #     output_video_path,
        #     settings.MEDIA_ROOT,
        # )
        # Open the file
        with open(output_video_path, "rb") as f:
            django_file = File(f)
            # Assign the file to the FileField
            videojob.output_video.save(
                os.path.basename(output_video_path), django_file, save=True
            )
        videojob.size = round(os.path.getsize(output_video_path) / (2**20), 2)

    videojob.save()


@shared_task
def censor_video(video_id):
    """Censor a video"""
    videojob = VideoJob.objects.select_related(
        "audio_setting",
        "video_setting",
    ).get(id=video_id)

    # Ensure dir for processed videos
    os.makedirs(
        os.path.dirname(videojob.get_output_video_path()),
        exist_ok=True,
    )

    processor = CensorshipProcessor(videojob)
    error_msg = None
    try:
        processor.run()
    except UserOutputError as e:
        error_msg = str(e)
        print(error_msg)
    except Exception as e:
        error_msg = "Unexpected error"
        print(str(e))
    finally:
        # Remove created result file if error occurs
        if error_msg and os.path.isfile(videojob.get_output_video_path()):
            os.remove(videojob.get_output_video_path())
        complete_videojob(videojob, error_msg)
