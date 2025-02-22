import numpy as np
import whisper
from pydub import AudioSegment

from errors.exceptions import TranscriptionError



class Transcriber:
    """Handles audio transcription using OpenAI's Whisper model"""
    
    def __init__(self, model_size: str = "tiny"):
        """
        Initialize Whisper model
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        try:
            self.model = whisper.load_model(model_size)
            self.sample_rate = 16000  # Whisper's expected sample rate
        except Exception as e:
            raise TranscriptionError.service_error(
                f"Failed to load model: {str(e)}"
            ) from e

    def transcribe(self, audio: AudioSegment) -> str:
        """
        Transcribe audio using Whisper
        Args:
            audio: Input audio segment
        Returns:
            str: Transcribed text
        Raises:
            TranscriptionError: For any transcription failure
        """
        try:
            # Convert to Whisper-compatible format
            audio = self._preprocess_audio(audio)
            result = self.model.transcribe(audio)
            
            if not result.get("text"):
                raise TranscriptionError.no_speech()
                
            return result["text"]
            
        except TranscriptionError:
            raise  # Re-raise already handled errors
        
        except Exception as e:
            raise TranscriptionError.generic_error(
                f"Transcription failed: {str(e)}"
            ) from e

    def _preprocess_audio(self, audio: AudioSegment) -> np.ndarray:
        """Convert AudioSegment to Whisper-compatible numpy array"""
        try:
            # Convert to mono and resample if needed
            audio = audio.set_channels(1)
            if audio.frame_rate != self.sample_rate:
                audio = audio.set_frame_rate(self.sample_rate)
                
            # Convert to numpy array of float32
            return np.frombuffer(
                audio.raw_data, 
                dtype=np.int16
            ).astype(np.float32) / 32768.0
            
        except Exception as e:
            raise TranscriptionError.generic_error(
                f"Audio preprocessing failed: {str(e)}"
            ) from e