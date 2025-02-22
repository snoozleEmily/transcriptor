import whisper


from .errors import TranscriptionError

class Transcriber:
    def __init__(self, model_size: str = "tiny"):
        self.model = whisper.load_model(model_size)
    
    def transcribe(self, audio: AudioSegment) -> str:
        """Transcribe audio using Whisper"""
        try:
            # Convert to Whisper-compatible format
            audio_array = audio.get_array_of_samples()
            return self.model.transcribe(
                audio_array.astype(np.float32)["text"]
        except Exception as e:
            raise TranscriptionError(str(e))