# Generated by Django 5.0.7 on 2024-08-06 17:49

import django.db.models.deletion
import videojobs.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profanity', models.BooleanField(blank=True, default=False)),
                ('xenophobia', models.BooleanField(blank=True, default=False)),
                ('own_words', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='VideoSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bad_habits', models.BooleanField(blank=True, default=False)),
                ('blood', models.BooleanField(blank=True, default=False)),
                ('nudity', models.BooleanField(blank=True, default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='VideoJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_videofile', models.FileField(upload_to=videojobs.models.get_input_videofile_path)),
                ('output_videofile', models.FileField(blank=True, null=True, upload_to=videojobs.models.get_output_videofile_path)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('size', models.FloatField(blank=True, null=True)),
                ('language', models.CharField(choices=[('EN', 'English'), ('RU', 'Russian')], max_length=2)),
                ('status', models.CharField(blank=True, choices=[('P', 'Processing'), ('S', 'Succeeded'), ('F', 'Failed')], default='P', max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('audio_setting', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='videojobs.audiosetting')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('video_setting', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='videojobs.videosetting')),
            ],
        ),
    ]
