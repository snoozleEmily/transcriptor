import whisper
import numpy as np
from tqdm import tqdm
from pydub import AudioSegment
from errors.exceptions import TranscriptionError

class Transcriber:
    """Audio transcription system using Whisper model"""
    
    def __init__(self, model_size: str = "tiny"):
        self.model = self._load_model(model_size)
        self.sample_rate = 16000  # Whisper's required sample rate

    def transcribe(self, audio_input=None, progress_handler=None) -> str:
        """Convert speech to text with progress updates"""
        audio = self._validate_input(audio_input)
        audio_array = self._convert_audio_format(audio)
        
        with tqdm(total=100, desc="Transcribing") as bar:
            result = self._run_transcription(
                audio_array,
                lambda p: self._update_progress(p, bar, progress_handler)
            )
        return self._validate_output(result)

    # --------------------- Core Pipeline ---------------------
    def _run_transcription(self, audio_buffer, progress_callback):
        """Execute transcription with version-safe progress"""
        try:
            # Try modern progress callback first
            return self._transcribe_with_progress(audio_buffer, progress_callback)
        except TypeError:
            # Fallback to basic transcription if progress fails
            return self.model.transcribe(audio_buffer)

    def _transcribe_with_progress(self, audio_buffer, progress_callback):
        """Modern progress-aware transcription"""
        duration = len(audio_buffer) / self.sample_rate
        
        def callback(segment, elapsed, total):
            percent = min((elapsed / duration) * 100, 100)
            progress_callback(percent)
            
        return self.model.transcribe(
            audio_buffer,
            progress_callback=callback,
            verbose=False
        )

    # --------------------- Progress Handling ---------------------
    def _update_progress(self, percent, tqdm_bar, external_handler):
        """Update both console and GUI progress"""
        tqdm_bar.n = percent
        if percent >= 99.9:
            tqdm_bar.set_description("Finished processing")
        tqdm_bar.refresh()
        
        if external_handler:
            external_handler(percent)

    # --------------------- Audio Processing ---------------------
    def _convert_audio_format(self, audio: AudioSegment) -> np.ndarray:
        """Convert to Whisper's expected FP32 mono format"""
        mono_audio = audio.set_channels(1)
        standardized = mono_audio.set_frame_rate(self.sample_rate)
        return np.frombuffer(
            standardized.raw_data, 
            np.int16
        ).astype(np.float32) / 32768.0  # PCM normalization

    # --------------------- Model Management ---------------------
    def _load_model(self, model_size: str):
        """Load Whisper model with validation"""
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if model_size not in valid_sizes:
            raise TranscriptionError.invalid_model()
            
        try:
            return whisper.load_model(model_size)
        except Exception as e:
            raise TranscriptionError.load_failed() from e

    # --------------------- Input/Output ---------------------
    def _validate_input(self, input_source):
        """Normalize audio input to PyDub format"""
        return input_source if isinstance(input_source, AudioSegment) \
            else AudioSegment.from_file(input_source)

    def _validate_output(self, result):
        """Ensure valid transcription result"""
        if not result.get("text"):
            raise TranscriptionError.no_speech()
        return result["text"]