# Generated by Django 5.0.8 on 2024-08-18 21:23

from django.db import migrations, models

import videojobs.models


class Migration(migrations.Migration):

    dependencies = [
        ('videojobs', '0011_alter_videojob_input_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videojob',
            name='input_video',
            field=models.FileField(upload_to=videojobs.models.get_input_video_path, validators=[videojobs.models.validate_input_video_extension, videojobs.models.validate_input_video_size]),
        ),
    ]
