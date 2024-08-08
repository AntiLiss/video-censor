# Generated by Django 5.0.7 on 2024-08-06 18:45

import videojobs.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videojobs', '0003_alter_videojob_audio_setting_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videojob',
            name='input_videofile',
            field=models.FileField(upload_to=videojobs.models.get_output_videofile_path),
        ),
    ]
