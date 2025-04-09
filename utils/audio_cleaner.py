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
        cleaned.tobytes(),         # The cleaned audio data
        frame_rate=audio.frame_rate,  # Keep original sample rate (e.g., 44100 Hz)
        sample_width=audio.sample_width,  # Keep original bit depth (e.g., 2 for 16-bit)
        channels=1                # Force mono output (single channel)
    )