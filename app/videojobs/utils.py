import subprocess

from faster_whisper import WhisperModel


class Singleton(type):
    _inctances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in Singleton._inctances:
            Singleton._inctances[cls] = super().__call__(*args, **kwargs)
        return Singleton._inctances[cls]


class WhisperModelSingleton(WhisperModel, metaclass=Singleton):
    """Singleton class ensuring only one instance of WhisperModel exists"""

    pass


def has_audio(video_path):
    """Check does the video have audio stream"""
    result = subprocess.run(
        [
            "ffprobe",
            "-i",
            video_path,
            "-show_streams",
            "-select_streams",
            "a",
            "-loglevel",
            "error",
        ],
        capture_output=True,
    )
    return True if result.stdout else False
