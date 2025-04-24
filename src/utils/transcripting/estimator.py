from scipy.stats import norm
from typing import Tuple


from src.utils.models import MODEL_SPEEDS, SETUP_TIMES


class TimeEstimator:
    """Handles all time estimation calculations for transcription"""
    # Constants for speech rate estimation
    WORDS_PER_SECOND_MEAN = 2.5    # Average words per second
    WORDS_PER_SECOND_STD = 0.5     # Standard deviation
    CONFIDENCE_LEVEL = 0.95        # Confidence interval level 
    CUSTOM_WORD_PENALTY = 0.005    # Slowdown factor per custom word

    def __init__(
        self, model_size: str, model_speeds: dict = None, setup_times: dict = None
    ):
        """
        Initialize time estimator for a specific model.

        Args:
            model_size: Name of the Whisper model size
            model_speeds: Optional custom speed dictionary
            setup_times: Optional custom setup times dictionary
        """
        self.model_size = model_size
        self.model_speeds = model_speeds or MODEL_SPEEDS
        self.setup_times = setup_times or SETUP_TIMES

        if model_size not in self.model_speeds:
            raise ValueError(f"Unknown model size: {model_size}") Add err to exceptions

    def estimate(
        self, audio_duration: float, custom_word_count: int = 0
    ) -> Tuple[float, float, float]:
        """
        Estimate transcription time with confidence interval.

        Args:
            audio_duration: Audio duration in seconds
            custom_word_count: Number of custom vocabulary words

        Returns:
            Tuple of (mean_time, low_ci_bound, high_ci_bound) in seconds
        """
        # Calculate word count estimates
        total_words_mean = audio_duration * self.WORDS_PER_SECOND_MEAN
        total_words_std = audio_duration * self.WORDS_PER_SECOND_STD

        # Calculate confidence interval
        ci_lower, ci_upper = self._calculate_confidence_interval(
            total_words_mean, 
            total_words_std
        )

        # Adjust for model speed and custom words
        actual_speed = self._get_adjusted_speed(custom_word_count)

        return (
            total_words_mean / actual_speed,
            ci_lower / actual_speed,
            ci_upper / actual_speed,
        )

    def get_setup_time(self) -> float:
        """Get the estimated setup time for the current model size."""
        return self.setup_times.get(self.model_size, 0)

    def _calculate_confidence_interval(
        self, mean_words: float, std_words: float
    ) -> Tuple[float, float]:
        """Calculate 95% confidence interval bounds."""
        two_tailed_alpha = (1 + self.CONFIDENCE_LEVEL) / 2  
        z_score = norm.ppf(two_tailed_alpha) 

        return (
            max(0.0, mean_words - z_score * std_words),
            mean_words + z_score * std_words,
        )

    def _get_adjusted_speed(self, custom_word_count: int) -> float:
        """Adjust transcription speed based on custom vocabulary."""
        base_speed = self.model_speeds[self.model_size]
        speed_reduction = 1 + (self.CUSTOM_WORD_PENALTY * custom_word_count)
        return base_speed / speed_reduction