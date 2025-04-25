import whisper
from src.utils.models import MODELS
from src.errors.handlers import TranscriptionError



class SetModel:
    """Manages Whisper model loading"""
    def load(self, model_size: str):
        if model_size not in MODELS:
            raise TranscriptionError.invalid_model()
            
        try:
            return whisper.load_model(model_size)
        
        except Exception as e:
            raise TranscriptionError.load_failed() from e