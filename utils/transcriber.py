import time
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
        
        with tqdm(
            total=100,
            desc="Transcribing",
            bar_format="{l_bar}{bar}| {n:.0f}%",
            miniters=1,
            mininterval=0,
            maxinterval=1
        ) as bar:
            result = self._run_transcription(
                audio_array,
                lambda p: self._update_progress(p, bar, progress_handler)
            )
            bar.n = 100  # Force completion
            bar.refresh()
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

    # --------------------- Progress Handling ---------------------
    def _transcribe_with_progress(self, audio_buffer, progress_callback):
        """Universal progress tracking for all Whisper versions"""
        # Get audio duration in seconds
        duration_seconds = len(audio_buffer) / self.sample_rate
        
        # Create progress tracking state
        progress_state = {
            'last_update': time.time(),
            'min_delta': 0.5,  # Minimum seconds between updates
            'last_percent': 0
        }

        def _handle_progress(*args):
            """Universal progress handler for different Whisper versions"""
            nonlocal duration_seconds
            
            # Calculate progress using whatever data we get
            if len(args) >= 3:  # Newer versions (segment, elapsed, total)
                _, elapsed, total = args[:3]
                if total > 0:
                    percent = min((elapsed / total) * 100, 100)
            else:  # Fallback for older versions
                current_time = time.time()
                time_elapsed = current_time - progress_state['start_time']
                percent = min((time_elapsed / duration_seconds) * 100, 100) if duration_seconds > 0 else 0

            # Throttle updates and ensure forward progress
            if (percent > progress_state['last_percent'] and 
                (current_time - progress_state['last_update']) > progress_state['min_delta']):
                progress_state['last_percent'] = percent
                progress_state['last_update'] = current_time
                progress_callback(percent)

        # Initialize timing
        progress_state['start_time'] = time.time()
        
        return self.model.transcribe(
            audio_buffer,
            progress_callback=_handle_progress,
            verbose=None  # Disable Whisper's internal prints
        )

    def _update_progress(self, percent, tqdm_bar, external_handler):
        """Universal progress updater"""
        # Calculate safe increment
        current = tqdm_bar.n
        new_value = min(max(percent, current + 1), 100)  # Force minimum 1% increments
        
        # Update tqdm if needed
        if new_value > current:
            tqdm_bar.update(new_value - current)
    

        # TODO: Need to implement interface loading bar    
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