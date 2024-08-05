from rest_framework.serializers import ModelSerializer
from .models import VideoJob, VideoSetting, AudioSetting


class VideoSettingSerializer(ModelSerializer):
    """VideoSetting serializer"""

    class Meta:
        model = VideoSetting
        fields = ("bad_habits", "blood", "nudity")


class AudioSettingSerializer(ModelSerializer):
    """AudioSetting serializer"""

    class Meta:
        model = AudioSetting
        fields = ("profanity", "xenophobia", "own_words")


class CreateVideoJobSerializer(ModelSerializer):
    """
    Serializer for creating a video task along with setting up
    associated instances
    """

    video_setting = VideoSettingSerializer(required=False)
    audio_setting = AudioSettingSerializer(required=False)

    class Meta:
        model = VideoJob
        fields = (
            "videofile",
            "title",
            "language",
            "video_setting",
            "audio_setting",
        )

    def create(self, validated_data):
        video_setting_data = validated_data.pop("video_setting")
        audio_setting_data = validated_data.pop("audio_setting")

        # Get existing same settings or create new
        video_setting, created = VideoSetting.objects.get_or_create(
            **video_setting_data,
        )
        audio_setting, created = AudioSetting.objects.get_or_create(
            **audio_setting_data,
        )

        return VideoJob.objects.create(
            video_setting=video_setting,
            audio_setting=audio_setting,
            **validated_data,
        )
