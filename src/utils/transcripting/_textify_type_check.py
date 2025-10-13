import time
import inspect
from typing import Dict, Optional, Callable, Any, Tuple, TYPE_CHECKING


from src.utils.text.content_type import ContentType
from src.logs.debug import debug



if TYPE_CHECKING:
    # Type-only imports (ignored at runtime)
    from .loader import Loader
    from .convert_audio import ConvertAudio
    from .info_dump import InfoDump
    from .estimator import TimeEstimator
    from .set_model import SetModel


class Textify:
    """Main transcription controller coordinating all components"""

    # Type hints for IDE and static analysis
    model: Optional[Any]
    progress: Optional["Loader"]
    audio_processor: Optional["ConvertAudio"]
    logger: Optional["InfoDump"]
    estimator: Optional["TimeEstimator"]
    use_on_progress: bool
    use_progress_callback: bool

    def __init__(self, model_size: str):
        self.model_size = model_size

        # Lazy load holders
        self.model = None
        self.progress = None
        self.audio_processor = None
        self.logger = None
        self.estimator = None
        self.use_on_progress = False
        self.use_progress_callback = False

        debug.dprint(
            f"Initialized Textify with model={self.model_size}, "
            f"use_on_progress={self.use_on_progress}, "
            f"use_progress_callback={self.use_progress_callback}"
        )

    def transcribe(
        self,
        audio_input: Optional[Any] = None,
        progress_handler: Optional[Callable[[float], None]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Main transcription pipeline"""
        progress, audio_processor, logger, estimator = self._init_helpers_if_needed()

        model = self._load_model_if_needed()

        start_time = time.time()
        duration = 0

        # Audio processing
        audio = audio_processor.validate_input(audio_input)
        audio_array, duration = audio_processor.convert(audio)

        debug.dprint(
            f"Audio validated. Duration={duration:.2f}s, "
            f"Shape={getattr(audio_array, 'shape', 'unknown')}"
        )

        # Time estimation
        content_config = kwargs.get("content_config", ContentType())
        custom_words = len(content_config.words) if content_config.words else 0
        setup_time = estimator.get_setup_time()

        debug.dprint(
            f"Estimation setup. Duration={duration:.2f}s, custom_words={custom_words}, "
            f"setup_time={setup_time:.2f}s"
        )

        pipeline_start = progress.setup(setup_time)
        if pipeline_start is None:
            pipeline_start = time.time()

        progress.start_transcription_progress(progress_handler)

        try:
            whisper_args: Dict[str, Any] = {
                "audio": audio_array,
                "temperature": kwargs.get("temperature", 0),
            }

            if progress.handler:
                current_handler = progress.handler

                if self.use_on_progress:
                    whisper_args["on_progress"] = lambda pct: current_handler(pct)

                elif self.use_progress_callback:
                    whisper_args["progress_callback"] = lambda pct: current_handler(pct)

            if "initial_prompt" in kwargs:
                whisper_args["initial_prompt"] = kwargs.pop("initial_prompt")

            # Filter out unsupported arguments
            supported_args = [
                "task",
                "language",
                "best_of",
                "beam_size",
                "patience",
                "length_penalty",
                "suppress_tokens",
                "condition_on_previous_text",
            ]
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in supported_args}
            safe_args = {k: v for k, v in whisper_args.items() if k != "audio"}

            debug.dprint(
                f"Calling transcribe with args={safe_args}, extra_kwargs={filtered_kwargs}"
            )

            result = model.transcribe(**whisper_args, **filtered_kwargs)

            return progress.complete(result, duration)

        finally:
            progress.active = False
            processing_time = time.time() - pipeline_start

            # Final progress update
            if progress.handler:
                progress.handler(100)

            logger.print_results(
                duration=duration,
                total_time=time.time() - start_time,
                transcribe_time=processing_time,
                speed_factor=duration / processing_time if processing_time > 0 else 0,
            )

    def _load_model_if_needed(self) -> Any:
        """
        Lazy-load the heavy model only when requested and return the concrete model instance.
        Returning the model avoids calling methods on a possibly-None attribute and so
        removes the need for asserts or casts at the call site.
        """
        if self.model is None:
            from .set_model import SetModel

            debug.dprint(f"Loading Whisper model: {self.model_size}")
            self.model = SetModel().load(self.model_size)
            self._detect_whisper_params()

        return self.model

    def _detect_whisper_params(self) -> None:
        """Determine correct progress parameter name for Whisper version"""
        # Narrow type for static checker: return early if model not loaded
        if self.model is None:
            # nothing to detect yet
            return

        transcribe_params = inspect.signature(self.model.transcribe).parameters
        self.use_on_progress = "on_progress" in transcribe_params
        self.use_progress_callback = "progress_callback" in transcribe_params

    def _init_helpers_if_needed(
        self,
    ) -> Tuple["Loader", "ConvertAudio", "InfoDump", "TimeEstimator"]:
        """Ensure helper objects exist and return them as concrete typed locals.

        Returning typed locals avoids Optional[...] member-access warnings from Pylance
        without introducing asserts or type:ignore everywhere.
        """
        if self.progress is None:
            from .loader import Loader as _Loader

            self.progress = _Loader()

        if self.audio_processor is None:
            from .convert_audio import ConvertAudio as _ConvertAudio

            self.audio_processor = _ConvertAudio()

        if self.logger is None:
            from .info_dump import InfoDump as _InfoDump

            self.logger = _InfoDump(self.model_size)

        if self.estimator is None:
            from .estimator import TimeEstimator as _TimeEstimator

            self.estimator = _TimeEstimator(self.model_size)

        return (self.progress, self.audio_processor, self.logger, self.estimator)
