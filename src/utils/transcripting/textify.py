import time
import inspect
from typing import Dict


from .loader import Loader
from .set_model import SetModel
from .info_dump import InfoDump
from .estimator import TimeEstimator
from .convert_audio import ConvertAudio
from src.utils.content_type import ContentType



class Textify:
    """Main transcription controller coordinating all components"""
    def __init__(self, model_size: str):
        self.model_size = model_size
        self.progress = Loader()
        self.audio_processor = ConvertAudio()        
        self.logger = InfoDump(model_size)
        self.model = SetModel().load(model_size)
        self.estimator = TimeEstimator(model_size)

        # Detect Whisper version parameters
        self._detect_whisper_params()

    def _detect_whisper_params(self):
        """Determine correct progress parameter name for Whisper version"""
        transcribe_params = inspect.signature(self.model.transcribe).parameters
        self.use_on_progress = 'on_progress' in transcribe_params
        self.use_progress_callback = 'progress_callback' in transcribe_params

    def transcribe(self, audio_input=None, progress_handler=None, **kwargs) -> Dict:
        """Main transcription pipeline"""
        start_time = time.time()

        # Audio processing
        audio = self.audio_processor.validate_input(audio_input)
        audio_array, duration = self.audio_processor.convert(audio)

        # Time estimation
        content_config = kwargs.get("content_config", ContentType())
        custom_words = len(content_config.words) if content_config.words else 0
        mean_t, lo_t, hi_t = self.estimator.estimate(duration, custom_words)
        setup_time = self.estimator.get_setup_time()

        # Progress setup
        self.progress.setup(setup_time, mean_t, progress_handler)
        pipeline_start = self.progress.show_setup_progress(setup_time)

        # Start transcription
        self.progress.start_transcription_progress(progress_handler)

        try:
            # Create version-safe transcription parameters
            whisper_args = {
                "audio": audio_array,
                "temperature": kwargs.get("temperature", 0.2),
            }

            # Handle initial prompt
            if "initial_prompt" in kwargs:
                whisper_args["initial_prompt"] = kwargs.pop("initial_prompt")

            # Add version-specific progress handler
            def progress_converter(p: float):
                # Convert between 0-1 and 0-100 based on version
                percent = p * 100 if self.use_on_progress else p
                self.progress.update(percent)

            if self.use_on_progress:
                whisper_args["on_progress"] = progress_converter
            elif self.use_progress_callback:
                whisper_args["progress_callback"] = progress_converter

            # Filter out unsupported arguments
            supported_args = [
                "task", "language", "best_of", "beam_size",
                "patience", "length_penalty", "suppress_tokens",
                "condition_on_previous_text"
            ]
            filtered_kwargs = {k: v for k, v in kwargs.items() 
                               if k in supported_args}

            result = self.model.transcribe(**whisper_args, **filtered_kwargs)

            # Finalize
            return self.progress.complete(result, duration)

        finally:
            self.progress.active = False
            self.logger.print_results(
                duration,
                time.time() - start_time,
                time.time() - pipeline_start,
                duration / (time.time() - pipeline_start) 
                if (time.time() - pipeline_start) > 0 
                else 0
            )