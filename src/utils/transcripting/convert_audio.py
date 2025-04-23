import numpy as np
from pydub import AudioSegment


class ConvertAudio:
    """Handles audio format conversion for Whisper"""

    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate  # Whisper's required rate

    def validate_input(self, input_source):
        return (
            input_source
            if isinstance(input_source, AudioSegment)
            else AudioSegment.from_file(input_source)
        )

    def convert(self, audio: AudioSegment) -> tuple:
        mono_audio = audio.set_channels(1)
        standardized = mono_audio.set_frame_rate(self.sample_rate)
        duration = len(standardized) / 1000  # Original duration calculation

        return (
            np.frombuffer(standardized.raw_data, np.int16).astype(np.float32) / 32768.0,
            duration,
        )
