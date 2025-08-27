import numpy as np
import noisereduce as nr
from pydub import AudioSegment


from src.errors.debug import debug



def clean_audio(audio: AudioSegment) -> AudioSegment:
    """Remove noise and silence"""
    debug.dprint(f"Original audio: frame_rate={audio.frame_rate}, sample_width={audio.sample_width}, channels={audio.channels}")
    
    samples = np.array(audio.get_array_of_samples())
    debug.dprint(f"Samples array shape: {samples.shape}")

    cleaned = nr.reduce_noise(y=samples, sr=audio.frame_rate)
    debug.dprint("Noise reduction complete")

    # Remove silence
    audio_seg = AudioSegment(
        cleaned.tobytes(),               # The cleaned audio data
        frame_rate=audio.frame_rate,     # Keep original sample rate (e.g., 44100 Hz)
        sample_width=audio.sample_width, # Keep original bit depth (e.g., 2 for 16-bit)
        channels=1                       # Force mono output (single channel)
    )
    debug.dprint(f"Returning cleaned audio: frame_rate={audio_seg.frame_rate}, sample_width={audio_seg.sample_width}, channels={audio_seg.channels}")
    
    return audio_seg
