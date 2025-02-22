import numpy as np
import noisereduce as nr
from pydub import AudioSegment
from pydub.silence import split_on_silence


def clean_audio(audio: AudioSegment) -> AudioSegment:
    """Remove noise and silence"""
    samples = np.array(audio.get_array_of_samples())
    cleaned = nr.reduce_noise(y=samples, sr=audio.frame_rate)
    
    # Remove silence
    return AudioSegment(
        cleaned.tobytes(),
        frame_rate=audio.frame_rate,
        sample_width=audio.sample_width,
        channels=1
    )