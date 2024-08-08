from rest_framework.serializers import ModelSerializer

from .models import AudioSetting, VideoJob, VideoSetting


class VideoSettingSerializer(ModelSerializer):
    """Video setting serializer"""

    class Meta:
        model = VideoSetting
        fields = ("bad_habits", "blood", "nudity")


class AudioSettingSerializer(ModelSerializer):
    """Audio setting serializer"""

    class Meta:
        model = AudioSetting
        fields = ("profanity", "xenophobia", "own_words")


class VideoJobReadSerializer(ModelSerializer):
    """Videojob read serializer"""

    class Meta:
        model = VideoJob
        fields = (
            "id",
            "output_videofile",
            "title",
            "size",
            "status",
        )


class VideoJobCreateSerializer(ModelSerializer):
    """
    Serializer to create a videojob along with setting up
    associated settings
    """

    video_setting = VideoSettingSerializer(required=False)
    audio_setting = AudioSettingSerializer(required=False)

    class Meta:
        model = VideoJob
        fields = (
            "id",
            "input_videofile",
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
            video_setting, created = VideoSetting.objects.get_or_create(
                **video_setting_data,
            )
            videojob.video_setting = video_setting
        if audio_setting_data:
            audio_setting, created = AudioSetting.objects.get_or_create(
                **audio_setting_data,
            )
            videojob.audio_setting = audio_setting

        videojob.save()
        return videojob
