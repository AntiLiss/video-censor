import os
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models


def get_input_videofile_path(instance, filename):
    """Generate path with unique filename for input video"""
    # extension = os.path.splitext(filename)[1]
    # filename = f"{uuid4()}{extension}"
    return os.path.join("uploads", "videos", filename)


def get_output_videofile_path(instance, filename):
    """Generate path with unique filename for output video"""
    extension = os.path.splitext(filename)[1]
    filename = filename + "_censored" + extension
    return os.path.join("processed_videos", filename)


class VideoJob(models.Model):
    # Status choices
    PROCESSING = "P"
    SUCCEEDED = "S"
    FAILED = "F"

    STATUS_CHOICES = (
        (PROCESSING, "Processing"),
        (SUCCEEDED, "Succeeded"),
        (FAILED, "Failed"),
    )

    # Language choices
    ENGLISH = "EN"
    RUSSIAN = "RU"

    LANG_CHOICES = (
        (ENGLISH, "English"),
        (RUSSIAN, "Russian"),
    )

    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE,
    )
    input_videofile = models.FileField(upload_to=get_input_videofile_path)
    output_videofile = models.FileField(
        upload_to=get_output_videofile_path,
        blank=True,
        null=True,
    )
    # TODO: Set to `filename` + "_censored" OR NOT??
    title = models.CharField(max_length=255, blank=True)
    size = models.FloatField(blank=True, null=True)
    language = models.CharField(max_length=2, choices=LANG_CHOICES)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=PROCESSING,
        blank=True,
    )
    video_setting = models.ForeignKey(
        "VideoSetting",
        null=True,
        on_delete=models.PROTECT,
    )
    audio_setting = models.ForeignKey(
        "AudioSetting",
        null=True,
        on_delete=models.PROTECT,
    )

    created_at = models.DateTimeField(auto_now_add=True)


class VideoSetting(models.Model):
    bad_habits = models.BooleanField(default=False, blank=True)
    blood = models.BooleanField(default=False, blank=True)
    nudity = models.BooleanField(default=False, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class AudioSetting(models.Model):
    profanity = models.BooleanField(default=False, blank=True)
    xenophobia = models.BooleanField(default=False, blank=True)
    own_words = models.TextField(
        blank=True,
        help_text="Comma separated string of words",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def get_own_word_set(self):
        """Get set of of own words"""
        return set(self.own_words.lower().split(","))


# {
#     "input_file": "my_video.mp4",
#     "title": "my_video",
#     "language": "EN",
#     "video_setting": {"blood": true},
#     "audio_setting": {"profanity": true, "own_words": ["idiot", "stupid"]},
# }
