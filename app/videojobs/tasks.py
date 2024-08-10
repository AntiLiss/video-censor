# import os
# import subprocess

# from celery import shared_task
# from django.conf import settings

# from .models import VideoJob


# @shared_task
# def reverse_video(video_id):
#     videojob = VideoJob.objects.get(id=video_id)
#     print("-" * 150)
#     print(videojob)
    # input_path = videojob.input_videofile.path
    # input_filename = os.path.basename(input_path)
    # name = os.path.splitext(input_filename)[0]
    # ext = os.path.splitext(input_filename)[1]

    # output_filename = name + "_censored" + ext
    # output_path = os.path.join(
    #     settings.MEDIA_ROOT,
    #     "processed_videos",
    #     output_filename,
    # )

    # command = f"ffmpeg -i {input_path} -vf reverse -af areverse {output_path}"
    # subprocess.run(command, shell=True, check=True)

    # videojob.output_videofile = output_path
    # videojob.status = videojob.SUCCEEDED
    # videojob.save()

    # return output_path
