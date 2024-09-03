import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


def get_input_video_path(instance, filename):
    """Generate path for input video"""
    return os.path.join("uploads", "videos", filename)


def validate_input_video_extension(value):
    """Check does the input file have valid extension"""
    ext = os.path.splitext(value.name)[1]
    valid_extensions = {".mp4", ".mkv", ".avi", ".mov"}
    if ext.lower() not in valid_extensions:
        raise ValidationError("Invalid file extension")


def validate_input_video_size(value):
    """Check does the input file size exceed the limit"""
    max_size_mb = 1024
    size_mb = round(value.size // (2**20), 2)
    # Error if file size exceeds max size
    if size_mb > max_size_mb:
        raise ValidationError(f"File size exceeds {max_size_mb}MB!")


class VideoJob(models.Model):
    # Status choices
    PROCESSING = "P"
    COMPLETED = "C"
    FAILED = "F"

    STATUS_CHOICES = (
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    )

    # Language choices
    ENGLISH = "en"
    RUSSIAN = "ru"

    LANG_CHOICES = (
        (ENGLISH, "English"),
        (RUSSIAN, "Russian"),
    )

    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE,
    )
    input_video = models.FileField(
        upload_to=get_input_video_path,
        validators=[
            validate_input_video_extension,
            validate_input_video_size,
        ],
    )
    output_video = models.FileField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
    size = models.FloatField(blank=True, null=True)
    language = models.CharField(max_length=2, choices=LANG_CHOICES)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=PROCESSING,
        blank=True,
    )
    error_message = models.TextField(blank=True)
    video_setting = models.ForeignKey(
        "VideoSetting",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    audio_setting = models.ForeignKey(
        "AudioSetting",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = self.get_title()
        return super().save(*args, **kwargs)

    def get_title(self):
        """Generate videojob's title value"""
        input_filename = os.path.basename(self.input_video.name)
        name = os.path.splitext(input_filename)[0]
        ext = os.path.splitext(input_filename)[1]
        return name + "_censored" + ext

    def get_output_video_path(self):
        """Generate absolute path for output file"""
        return os.path.join(
            settings.MEDIA_ROOT,
            "processed_videos",
            self.get_title(),
        )


class VideoSetting(models.Model):
    smoking = models.BooleanField(default=False, blank=True)
    gore = models.BooleanField(default=False, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_applied(self):
        """Check if any field is set"""
        return any((self.smoking, self.gore))


class AudioSetting(models.Model):
    profanity = models.BooleanField(default=False, blank=True)
    insult = models.BooleanField(default=False, blank=True)
    own_words = models.TextField(
        blank=True,
        help_text="Comma separated string of words",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_own_word_set(self):
        """Get set of own words"""
        word_str = self.own_words.lower().strip()
        word_list = [w for w in word_str.split(",") if w]
        return set(word_list)

    def is_applied(self):
        """Check if any field is set"""
        return any((self.profanity, self.insult, self.own_words))
