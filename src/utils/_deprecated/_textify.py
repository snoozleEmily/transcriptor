# Deprecated

import time
import whisper
import threading
import numpy as np
from tqdm import tqdm
from pydub import AudioSegment
from scipy.stats import norm


from src.errors.exceptions import TranscriptionError
from src.utils.content_type import ContentType
from src.utils.models import MODELS, MODEL_SPEEDS, SETUP_TIMES



class Textify:  # called Transcriptor before
    """Audio transcription system using Whisper model"""

    SPEECH_RATE_MU = 2.5
    SPEECH_RATE_SIGMA = 0.5
    CI_LEVEL = 0.95

    def __init__(self, model_size: str):
        self.models_speeds = MODEL_SPEEDS
        self.setup_times = SETUP_TIMES

        self.model_size = model_size
        self.model = self._load_model(model_size)

        self.sample_rate = 16000  # Whisper's required sample rate
        self._progress_active = False  # Flag for duration-based progress
        self.estimated_total_time = 0

    def transcribe(self, audio_input=None, progress_handler=None, **kwargs) -> dict:
        """Convert speech to text with progress updates and time estimation"""
        original_start = time.time()
        audio = self._validate_input(audio_input)
        audio_array, duration = self._convert_audio_format(audio)

        content_config = kwargs.get("content_config", ContentType())
        custom_words = (
            len(content_config.words) if content_config and content_config.words else 0
        )

        mean_t, lo_t, hi_t = self._estimate_transcription_time(duration, custom_words)
        setup_time = self.setup_times.get(self.model_size, 0)
        self.estimated_total_time = setup_time + mean_t

        # Show setup progress for medium/large models
        if setup_time > 0:
            self._log_estimate(duration, setup_time, mean_t, lo_t, hi_t)

            with tqdm(
                total=setup_time,
                desc="Initializing Model",
                bar_format="\n{l_bar}| {n:.1f}/{total:.1f}s",
                unit="s",
            ) as setup_bar:
                for _ in range(int(setup_time)):
                    time.sleep(1)
                    setup_bar.update(1)
            pipeline_start = time.time()

        else:
            pipeline_start = original_start

        with tqdm(
            total=100,
            desc="\nTranscribing",
            bar_format="{l_bar}| {n:.0f}%",
            miniters=1,
            mininterval=0,
            maxinterval=1,
        ) as bar:
            self._progress_active = True

            # start time-based estimator
            progress_thread = threading.Thread(
                target=self._update_progress_estimate,
                args=(bar, pipeline_start, progress_handler),
            )
            progress_thread.start()

            # watchdog to force completion
            watchdog_thread = threading.Thread(
                target=self._watchdog,
                args=(bar, progress_handler),
            )
            watchdog_thread.daemon = True
            watchdog_thread.start()

            # delay indicator when stuck at 99%
            def _delay_indicator():
                interval = 2.6  # Bar tick (in seconds)

                while self._progress_active and bar.n > 99:
                    time.sleep(0.1)

                if self._progress_active and bar.n > 100:
                    print("ETA: {remaining}")
                    print(
                        "\n\n⚠️ Transcription is taking longer than usual, but this is expected.\n"
                        "⏳ Please be patient and DO NOT close the app.\n\n"
                    )

                if self._progress_active:
                    with tqdm(
                        total=self.estimated_total_time,
                        desc="[DELAY] Still Transcribing",
                        bar_format="{l_bar} | Elapsed: {elapsed} seconds",
                        unit="s",
                        leave=False,
                    ) as delay_bar:
                        while self._progress_active:
                            time.sleep(interval)
                            delay_bar.update(interval)

            delay_thread = threading.Thread(target=_delay_indicator)
            delay_thread.daemon = True
            delay_thread.start()

            try:
                transcribe_start = time.time()
                result = self._run_transcription(
                    audio_array,
                    lambda p: self._update_progress(p, bar, progress_handler),
                    **kwargs,
                )
                transcribe_time = time.time() - transcribe_start
                total_time = time.time() - pipeline_start
                speed_factor = duration / transcribe_time if transcribe_time > 0 else 0

                # event-driven final update
                bar.update(100 - bar.n)
                if progress_handler:
                    progress_handler(100)

            finally:
                self._progress_active = False
                progress_thread.join()
                delay_thread.join()

            bar.n = 100  # Force completion
            bar.refresh()

            result["metadata"] = {
                "audio_duration": duration,
                "processing_time": total_time,
                "transcription_time": transcribe_time,
                "speed_factor": speed_factor,
            }

            self._print_results(duration, total_time, transcribe_time, speed_factor)

            return self._validate_output(result)

    def _estimate_transcription_time(
        self, duration: float, custom_words: int
    ) -> tuple[float, float, float]:
        mu_words = duration * self.SPEECH_RATE_MU
        sigma_words = duration * self.SPEECH_RATE_SIGMA
        alpha = (1 + self.CI_LEVEL) / 2
        z = norm.ppf(alpha)
        lower_words = max(0.0, mu_words - z * sigma_words)
        upper_words = mu_words + z * sigma_words

        base_speed = self.models_speeds.get(self.model_size, 1)
        penalty = 1 + 0.005 * custom_words
        adjusted_speed = base_speed / penalty

        mean_t = mu_words / adjusted_speed
        lo_t = lower_words / adjusted_speed
        hi_t = upper_words / adjusted_speed
        return mean_t, lo_t, hi_t

    # --------------------- Logs ---------------------
    def _log_estimate(self, duration, setup, mean_t, lo_t, hi_t):
        """Display estimation details with confidence interval"""
        CURRENT_MODEL = {self.model_size.upper()}

        print("\n📏 [ESTIMATION METRICS]")
        print(f"  🔊 Audio Duration: {duration:.1f}s")
        print(f"  🎥  Used Model : {CURRENT_MODEL}")
        print(f"  ⚙️  Model Setup: {setup:.1f}s")
        print(
            f"  ✍️  Transcription Estimate: {mean_t:.1f}s (95% CI: {lo_t:.1f}-{hi_t:.1f}s)"
        )
        print(f"  🕛 Total Estimated: {setup + mean_t:.1f}s")

    def _print_results(self, duration, total_time, transcribe_time, speed_factor):
        """Display beautiful formatted results with emojis"""
        print("\n" + "✨" * 14)
        print(f"🎉 Transcription Complete! 🎉")
        print("✨" * 14)
        print("\n" + "-" * 22)
        print(f"📝 [TIME REPORT]")
        print(f"🔊 Audio Duration: {duration:.2f} seconds")
        print(f"⏱️ Total Processing: {total_time:.2f} seconds")
        print(f"✍️ Pure Transcription: {transcribe_time:.2f} seconds")
        print(f"🚀 Speed: {speed_factor:.2f}x real-time")
        print("-" * 22)
        print(f"\n✏️ Results Ready! ✏️")

    # --------------------- Core Pipeline ---------------------
    def _run_transcription(self, audio_buffer, progress_callback, **kwargs):
        """Execute transcription with version-safe progress"""
        try:
            return self._transcribe_with_progress(
                audio_buffer, progress_callback, **kwargs
            )
        except TypeError:
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
        while self._progress_active and bar.n < 99:
            time.sleep(1)
            bar.update(min(increment, 99 - bar.n))
            if handler:
                handler(bar.n)

    def _watchdog(self, bar, handler):
        """Force-progress ensures final completion"""
        time.sleep(self.estimated_total_time + 1)
        if self._progress_active and bar.n < 100:
            bar.update(100 - bar.n)
            if handler:
                handler(100)

    def _update_progress_estimate(self, bar, start_time, handler):
        """Update progress based on time estimates"""
        while self._progress_active and bar.n < 99:
            elapsed = time.time() - start_time
            progress = min((elapsed / self.estimated_total_time) * 100, 99)
            if progress > bar.n:
                bar.update(progress - bar.n)
                if handler:
                    handler(progress)
            time.sleep(0.2)

    def _update_progress(self, percent, tqdm_bar, progress_handler):
        """Universal progress updater"""
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
        models = MODELS
        if model_size not in models:
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
        return result
