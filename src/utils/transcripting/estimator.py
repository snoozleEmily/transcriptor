from scipy.stats import norm
from typing import Tuple


from src.utils.models import MODEL_SPEEDS, SETUP_TIMES



class TimeEstimator:
    """Handles all time estimation calculations for transcription"""

    # Constants for speech rate estimation
    SPEECH_RATE_MU = 2.5  # Average words per second
    SPEECH_RATE_SIGMA = 0.5  # Standard deviation
    CI_LEVEL = 0.95  # Confidence interval level
    CUSTOM_WORD_PENALTY = 0.005  # Slowdown factor per custom word

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
            raise ValueError(f"Unknown model size: {model_size}")

    def estimate(
        self, duration: float, custom_word_count: int = 0
    ) -> Tuple[float, float, float]:
        """
        Estimate transcription time with confidence interval.

        Args:
            duration: Audio duration in seconds
            custom_word_count: Number of custom vocabulary words

        Returns:
            Tuple of (mean_time, low_ci, high_ci) in seconds
        """
        # Calculate word count estimates
        mu_words = duration * self.SPEECH_RATE_MU
        sigma_words = duration * self.SPEECH_RATE_SIGMA

        # Calculate confidence interval
        lower_words, upper_words = self._calculate_confidence_interval(
            mu_words, sigma_words
        )

        # Adjust for model speed and custom words
        adjusted_speed = self._get_adjusted_speed(custom_word_count)

        return (
            mu_words / adjusted_speed,
            lower_words / adjusted_speed,
            upper_words / adjusted_speed,
        )

    def get_setup_time(self) -> float:
        """Get the estimated setup time for the model"""
        return self.setup_times.get(self.model_size, 0)

    def _calculate_confidence_interval(
        self, mu: float, sigma: float
    ) -> Tuple[float, float]:
        """Calculate 95% confidence interval bounds"""
        alpha = (1 + self.CI_LEVEL) / 2
        z = norm.ppf(alpha)
        return (max(0.0, mu - z * sigma), mu + z * sigma)

    def _get_adjusted_speed(self, custom_word_count: int) -> float:
        """Calculate speed adjusted for custom vocabulary"""
        base_speed = self.model_speeds[self.model_size]
        penalty_factor = 1 + (self.CUSTOM_WORD_PENALTY * custom_word_count)
        return base_speed / penalty_factor
