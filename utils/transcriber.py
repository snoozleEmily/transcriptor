import numpy as np
import whisper
from pydub import AudioSegment
from typing import Optional, Callable


from errors.exceptions import TranscriptionError



class Transcriber:
    """Handle audio transcription using Whisper"""
    
    def __init__(self, model_size: str = "tiny"):
        self.model = self._load_model(model_size)
        self.sample_rate = 16000

    def transcribe(self, audio_input, progress_cb: Optional[Callable[[int], None]] = None) -> str:
        # If the input is already an AudioSegment, use it directly.
        if isinstance(audio_input, AudioSegment):
            audio = audio_input
        else:
            audio = self._load_audio(audio_input)
        
        audio_array = self._preprocess_audio(audio)
        
        self._update_progress(progress_cb, 10)
        
        result = self.model.transcribe(audio_array)
        
        self._update_progress(progress_cb, 100)
        
        if not result.get("text"):
            raise TranscriptionError.no_speech()
            
        return result["text"]


    def _load_model(self, model_size: str):
        """Load Whisper model with validation"""
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if model_size not in valid_sizes:
            raise TranscriptionError.invalid_model()
            
        try:
            return whisper.load_model(model_size)
        except Exception as e:
            raise TranscriptionError.load_failed() from e

    def _load_audio(self, path: str) -> AudioSegment:
        """Load and validate audio file"""
        try:
            audio = AudioSegment.from_file(path)
            if len(audio) == 0:
                raise TranscriptionError.empty_audio()
            return audio
        
        except Exception as e:
            raise TranscriptionError.load_failed() from e

    def _preprocess_audio(self, audio: AudioSegment) -> np.ndarray:
        """Convert audio to Whisper-compatible format"""
        try:
            audio = audio.set_channels(1).set_frame_rate(self.sample_rate)
            return np.frombuffer(audio.raw_data, np.int16).astype(np.float32) / 32768.0
        except Exception as e:
            raise TranscriptionError.preprocessing_failed() from e

    def _handle_progress(self, progress: float, callback: Optional[Callable[[int], None]]):
        if callback:
            callback(min(100, int(progress * 100)))

    def _update_progress(self, callback: Optional[Callable[[int], None]], value: int):
        if callback:
            callback(value)