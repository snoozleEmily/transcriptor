import whisper


from src.logs.debug import debug
from src.logs.exceptions import TranscriptionError
from src.utils.models import WHISPER_MODELS



class SetModel:
    """Manages Whisper model loading"""
    def load(self, model_size: str):
        debug.dprint(f"Requested Whisper model: {model_size}")

        if model_size not in WHISPER_MODELS:
            raise TranscriptionError.invalid_model()
            
        try:
            model = whisper.load_model(model_size)
            debug.dprint(f"Successfully loaded model: {model_size} of type: {type(model)}")
            return model
        
        except Exception as e:
            raise TranscriptionError.load_failed() from e
