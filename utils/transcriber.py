import numpy as np
import whisper
from pydub import AudioSegment


from errors.exceptions import TranscriptionError



class Transcriber:
    """Handle audio transcription using Whisper"""
    
    def __init__(self, model_size: str = "tiny"):
        self.model = self._load_model(model_size)
        self.sample_rate = 16000

    def transcribe(self, audio_input=None) -> str:
        """Execute full transcription pipeline"""
        # Audio input handling
        if isinstance(audio_input, AudioSegment):
            audio = audio_input
        else:
            audio = self._load_audio(audio_input)
        
        # Audio processing
        audio_array = self._preprocess_audio(audio)
        
        # Core transcription
        result = self.model.transcribe(audio_array)
        
        # Result validation
        if not result.get("text"):
            raise TranscriptionError.no_speech()
            
        return result["text"]

    # --------------------- Core Components ---------------------
    def _load_model(self, model_size: str):
        """Initialize Whisper model with validation"""
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if model_size not in valid_sizes:
            raise TranscriptionError.invalid_model()
            
        try:
            return whisper.load_model(model_size)
        except Exception as e:
            raise TranscriptionError.load_failed() from e

    # --------------------- Audio Processing ---------------------
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
            return np.frombuffer(
                audio.raw_data, 
                np.int16
            ).astype(np.float32) / 32768.0
        except Exception as e:
            raise TranscriptionError.preprocessing_failed() from e