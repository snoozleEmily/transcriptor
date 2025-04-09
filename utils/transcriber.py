import time
import whisper
import threading
import numpy as np
from tqdm import tqdm
from pydub import AudioSegment


from errors.exceptions import TranscriptionError



class Transcriber:
    """Audio transcription system using Whisper model"""

    def __init__(self, model_size: str = "tiny"):
        self.model = self._load_model(model_size)
        self.sample_rate = 16000  # Whisper's required sample rate
        self._progress_active = False  # Flag for duration-based progress

    def transcribe(self, audio_input=None, progress_handler=None) -> str:
        """Convert speech to text with progress updates"""
        audio = self._validate_input(audio_input)
        audio_array, duration = self._convert_audio_format(audio)

        with tqdm(
            total=100,
            desc="Transcribing",
            bar_format="{l_bar}{bar}| {n:.0f}%",
            miniters=1,
            mininterval=0,
            maxinterval=1,
        ) as bar:
            # Start duration-based progress thread
            self._progress_active = True
            duration_thread = threading.Thread(
                target=self._duration_progress,
                args=(bar, duration, progress_handler))
            duration_thread.start()

            try:
                result = self._run_transcription(
                    audio_array, 
                    lambda p: self._update_progress(p, bar, progress_handler))
            finally:
                self._progress_active = False
                duration_thread.join()

            bar.n = 100  # Force completion
            bar.refresh()
            return self._validate_output(result)

    # --------------------- Core Pipeline ---------------------
    def _run_transcription(self, audio_buffer, progress_callback):
        """Execute transcription with version-safe progress"""
        try:
            # Try modern progress callback first
            return self._transcribe_with_progress(audio_buffer, progress_callback)
        except TypeError as e:
            # Fallback if progress callback fails
            return self.model.transcribe(audio_buffer)

    # --------------------- Progress Handling ---------------------
    def _transcribe_with_progress(self, audio_buffer, progress_callback):
        """Universal progress tracking for all Whisper versions"""
        return self.model.transcribe(
            audio_buffer,
            progress_callback=progress_callback,
            verbose=None,  # Disable Whisper's internal prints
        )

    def _duration_progress(self, bar, total_duration, handler):
        """Time-based progress using audio duration estimate"""
        increment = 100 / total_duration  # Percent per second
        while self._progress_active and bar.n < 95:
            time.sleep(1)
            bar.update(min(increment, 100 - bar.n))
            if handler:
                handler(bar.n)

    def _update_progress(self, percent, tqdm_bar, progress_handler):
        """Universal progress updater"""
        # Calculate safe increment
        current = tqdm_bar.n
        new_value = min(max(percent, current + 1), 100)  # Force minimum 1% increments

        if new_value > current:
            tqdm_bar.update(new_value - current)
        if progress_handler:
            progress_handler(new_value)

    # --------------------- Audio Processing ---------------------
    def _convert_audio_format(self, audio: AudioSegment) -> tuple[np.ndarray, float]:
        """Convert to Whisper's expected FP32 mono format"""
        mono_audio = audio.set_channels(1)
        standardized = mono_audio.set_frame_rate(self.sample_rate)
        duration = len(standardized) / 1000  # Duration in seconds
        return (
            np.frombuffer(standardized.raw_data, np.int16).astype(np.float32) / 32768.0,
            duration
        )

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
        return (
            input_source
            if isinstance(input_source, AudioSegment)
            else AudioSegment.from_file(input_source)
        )

    def _validate_output(self, result):
        """Ensure valid transcription result"""
        if not result.get("text"):
            raise TranscriptionError.no_speech()
        return result["text"]