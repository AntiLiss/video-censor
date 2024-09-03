import re

from rest_framework.serializers import ModelSerializer, ValidationError

from .models import AudioSetting, VideoJob, VideoSetting


class VideoSettingSerializer(ModelSerializer):
    """Video setting serializer"""

    class Meta:
        model = VideoSetting
        fields = ("smoking", "gore")
        extra_kwargs = {
            "smoking": {"default": False},
            "gore": {"default": False},
        }


class AudioSettingSerializer(ModelSerializer):
    """Audio setting serializer"""

    class Meta:
        model = AudioSetting
        fields = ("profanity", "insult", "own_words")
        extra_kwargs = {
            "profanity": {"default": False},
            "insult": {"default": False},
            "own_words": {"default": ""},
        }

    def validate_own_words(self, own_words):
        """Check is the value a comma separated word string"""
        own_words = own_words.strip()
        # The string consists at least of 1 word.
        # Words are separated by comma.
        # Word consists of letters and/or digits.
        # Words united by `-` like `co-op` are allowed
        pattern = r"\b\w+(-\w+)*\b(,\b\w+(-\w+)*\b)*,?"

        if own_words and (
            not re.fullmatch(pattern, own_words) or re.search(r"_", own_words)
        ):
            msg = "Ensure this is a comma separated list of words!"
            raise ValidationError(msg)

        return own_words


class VideoJobReadSerializer(ModelSerializer):
    """Videojob read serializer"""

    class Meta:
        model = VideoJob
        fields = (
            "id",
            "title",
            "output_video",
            "size",
            "status",
            "error_message",
        )


class VideoJobCreateSerializer(ModelSerializer):
    """
    Serializer to create a videojob along with setting up associated settings
    """

    video_setting = VideoSettingSerializer(required=False)
    audio_setting = AudioSettingSerializer(required=False)

    class Meta:
        model = VideoJob
        fields = (
            "id",
            "input_video",
            "language",
            "video_setting",
            "audio_setting",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        video_setting_data = validated_data.pop("video_setting", None)
        audio_setting_data = validated_data.pop("audio_setting", None)
        videojob = VideoJob.objects.create(**validated_data)

        # Get existing settings or create new
        if video_setting_data:
            video_setting, _ = VideoSetting.objects.get_or_create(
                **video_setting_data,
            )
            videojob.video_setting = video_setting

        if audio_setting_data:
            audio_setting, _ = AudioSetting.objects.get_or_create(
                **audio_setting_data,
            )
            videojob.audio_setting = audio_setting

        videojob.save()
        return videojob
