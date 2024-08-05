import os
from uuid import uuid4
from django.db import models


def get_uploaded_videofile_path(instance, filename):
    """Generate videofile path with unique uuid filename"""
    extension = os.path.splitext(filename)[1]
    filename = f"{uuid4()}{extension}"
    return os.path.join("uploads", "videos", filename)


def get_processed_videofile_path(instance, filename):
    """Generate video file path for processed video"""
    extension = os.path.splitext(filename)[1]
    filename = os.path.splitext(filename)[0] + "_censored" + extension
    return os.path.join("uploads", "processed_videos", filename)


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

    videofile = models.FileField(upload_to=get_uploaded_videofile_path)
    title = models.CharField(max_length=255)
    size = models.FloatField(blank=True)
    language = models.CharField(max_length=2, choices=LANG_CHOICES)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=PROCESSING,
        blank=True,
    )
    video_setting = models.ForeignKey(
        "VideoSetting",
        on_delete=models.PROTECT,
    )
    audio_setting = models.ForeignKey(
        "AudioSetting",
        on_delete=models.PROTECT,
    )


class VideoSetting(models.Model):
    bad_habits = models.BooleanField(default=False, blank=True)
    blood = models.BooleanField(default=False, blank=True)
    nudity = models.BooleanField(default=False, blank=True)


class AudioSetting(models.Model):
    profanity = models.BooleanField(default=False, blank=True)
    xenophobia = models.BooleanField(default=False, blank=True)
    # A list of own words, don't forget to check UNIQUENESS!
    own_words = models.JSONField(default=list, blank=True)


# {
#     "videofile": "my_video.mp4",
#     "title": "my_video",
#     "language": "EN",
#     "video_setting": {"blood": true},
#     "audio_setting": {"profanity": true, "own_words": ["idiot", "stupid"]},
# }
