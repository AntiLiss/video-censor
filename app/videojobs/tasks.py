import os
import subprocess

import ffmpeg
from celery import shared_task
import whisperx
from django.conf import settings

from .models import VideoJob


@shared_task
def reverse_video(video_id):
    videojob = VideoJob.objects.get(id=video_id)

    input_path = videojob.input_video.path
    # output_path = videojob.get_output_video_path()
    # output_dir = os.path.dirname(output_path)
    # # Create a dir branch for processed videos if not present
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    # ffmpeg.input(input_path).output(
    #     output_path,
    #     vcodec="libx264",
    #     crf=18,
    #     preset="veryslow",
    #     acodec="aac",
    #     audio_bitrate="320k",
    #     vf="reverse",
    #     af="areverse",
    # ).run()

    # relative_output_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
    # videojob.output_video = relative_output_path
    # videojob.size = round(os.path.getsize(output_path) / (2**20), 2)
    # videojob.status = videojob.COMPLETED
    # videojob.save()




    device = "cpu"
    compute_type = "int8"
    batch_size = 16

    # 1. Transcribe with original whisper (batched)
    model = whisperx.load_model(
        "small",
        device="cpu",
        compute_type="int8",
    )
    audio = whisperx.load_audio(input_path)
    result = model.transcribe(audio, batch_size=batch_size, language="ru")

    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"],
        device=device,
    )
    result = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )

    print(result["word_segments"])

    string = ""
    for seg in result["word_segments"]:
        string += seg["word"] + " "
    print((string))

    videojob.text = string
    videojob.save()

    return "MY RESULT!!!"
