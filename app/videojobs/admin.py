from django.contrib import admin

from .models import AudioSetting, VideoJob, VideoSetting

admin.site.register(VideoJob)
admin.site.register(AudioSetting)
admin.site.register(VideoSetting)
