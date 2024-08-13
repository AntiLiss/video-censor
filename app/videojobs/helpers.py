from faster_whisper import WhisperModel
import string


def transcribe_with_timestamps(
    file_path, lang, model_size="medium", device="cpu", compute_type="int8"
):
    """
    Transcribe video/audio file and return dictionary of timestamps for each
    word
    """
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _ = model.transcribe(
        file_path,
        language=lang,
        word_timestamps=True,
    )

    word_objects = []
    for segment in segments:
        word_objects += segment.words

    word_timings = {}
    for w in word_objects:
        key = w.word.translate(str.maketrans("", "", string.punctuation))
        key = key.lower().strip()
        if key in word_timings:
            word_timings[key].append((w.start, w.end))
            continue
        word_timings[key] = [(w.start, w.end)]

    return word_timings


def beep_audio():
    pass
