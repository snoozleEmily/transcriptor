import time
import whisper
import threading
import numpy as np
from tqdm import tqdm
from pydub import AudioSegment


from src.errors.exceptions import TranscriptionError
from src.utils.content_type import ContentType

# TODO: Update model_size to be in tune with models in EndFlow


class Textify:  # called Transcriptor before
    """Audio transcription system using Whisper model"""

    def __init__(self, model_size: str = "tiny"):
        self.model = self._load_model(model_size)
        self.sample_rate = 16000  # Whisper's required sample rate
        self._progress_active = False  # Flag for duration-based progress

    def transcribe(
        self, audio_input=None, progress_handler=None, **kwargs
    ) -> dict:  # chanded to dict from str because of breaking change
        """Convert speech to text with progress updates"""
        pipeline_start = time.time()

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
                target=self._duration_progress, args=(bar, duration, progress_handler)
            )
            duration_thread.start()

            try:
                # Core transcription
                transcribe_start = time.time()
                result = self._run_transcription(
                    audio_array,
                    lambda p: self._update_progress(p, bar, progress_handler),
                    **kwargs,  # For custom words
                )
                transcribe_time = time.time() - transcribe_start

            finally:
                self._progress_active = False
                duration_thread.join()

            bar.n = 100  # Force completion
            bar.refresh()

    # --------------------- Time Measurement Printing ---------------------

            # Calculate timing metrics
            total_time = time.time() - pipeline_start
            speed_factor = duration / transcribe_time if transcribe_time > 0 else 0

            # Store all timing data
            result["metadata"] = {
                "audio_duration": duration,
                "processing_time": total_time,
                "transcription_time": transcribe_time,
                "speed_factor": speed_factor,
            }

            # Print pretty results
            self._print_results(duration, total_time, transcribe_time, speed_factor)

            return self._validate_output(result)

    def _print_results(
        self,
        duration: float,
        total_time: float,
        transcribe_time: float,
        speed_factor: float,
    ):
        """Display beautiful formatted results with emojis"""
        print("\n")
        print("-" * 14 + "\n")
        print("✨" * 14)
        print(f"          🎉 Transcription Complete! 🎉")
        print("✨" * 14)
        print("-" * 14 + "\n")
        print(f"[TIME REPORT]")
        print(f"\n🔊 Audio Duration: {duration:.2f} seconds")
        print(f"⏱️ Total Processing: {total_time:.2f} seconds")
        print(f"✍️ Pure Transcription: {transcribe_time:.2f} seconds")
        print(f"🚀 Speed: {speed_factor:.2f}x real-time")
        print("-" * 14 + "\n")
        print(f"          ✏️ Results Ready! ✏️")
        print("-" * 14 + "\n")

    # --------------------- Core Pipeline ---------------------
    def _run_transcription(self, audio_buffer, progress_callback, **kwargs):
        """Execute transcription with version-safe progress"""
        try:
            # Try modern progress callback first
            return self._transcribe_with_progress(
                audio_buffer, progress_callback, **kwargs  # For custom words
            )

        except TypeError as e:
            # Fallback if progress callback fails
            return self.model.transcribe(audio_buffer, **kwargs)

    # --------------------- Handle Custom Words ---------------------
    def _get_content_prompt(self, content_config: ContentType) -> str:
        """Generate context prompt based on content configuration"""
        prompt_parts = []

        if content_config.words:
            print(
                f"[DEBUGGER] The transcript has specific words: \n",
                content_config.words,
            )
            if content_config.words:
                prompt_parts.append(f"Domains: {', '.join(content_config.words)}")

        if content_config.has_code:
            print(f"[DEBUGGER] Code detected: \n", content_config.has_code)

        if content_config.has_odd_names:
            print(f"[DEBUGGER] Odd names detected: \n", content_config.has_odd_names)

        return " ".join(prompt_parts)

    # --------------------- Progress Handling ---------------------
    def _transcribe_with_progress(self, audio_buffer, progress_callback, **kwargs):
        """Universal progress tracking for all Whisper versions"""
        return self.model.transcribe(
            audio_buffer,
            progress_callback=progress_callback,
            verbose=None,  # Disable Whisper's internal prints
            **kwargs,  # For custom words
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
            duration,
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
        return result  # ["text"] for now this is a BREAKING CHANGE
