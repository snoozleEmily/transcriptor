from typing import Optional, Union



class InfoDump:
    """Handles all logging, progress reporting, and output formatting"""

    def __init__(self, model_size: Optional[str] = None):
        self.model_size = str(model_size)
        self.emoji_width = 14  # For decorative formatting

    def log_estimate(
        self,
        duration: Union[float, str],
        setup_time: float,
        mean_time: float,
        low_ci: float,
        high_ci: float,
    ):
        """
        Display estimation details with confidence interval

        Args:
            duration: Audio duration in seconds
            setup_time: Model loading time estimate
            mean_time: Average expected transcription time
            low_ci: Lower bound of confidence interval
            high_ci: Upper bound of confidence interval
        """
        title = "📏 [ESTIMATION METRICS]"
        items = [
            f"🔊 Audio Duration: {str(duration):.1f}s",
            f"🎥 Used Model: {self.model_size.upper()}",
            f"⚙️ Model Setup: {setup_time:.1f}s",
            f"✍️ Transcription Estimate: {mean_time:.1f}s (95% CI: {low_ci:.1f}-{high_ci:.1f}s)",
            f"🕛 Total Estimated: {setup_time + mean_time:.1f}s",
        ]

        print(f"\n{title}")
        for item in items:
            print(f"  {item}")

    def print_results(
        self,
        duration: float,
        total_time: float,
        transcribe_time: float,
        speed_factor: float,
    ):
        """
        Display final transcription results with formatting

        Args:
            duration: Original audio duration
            total_time: Total processing time
            transcribe_time: Actual transcription time
            speed_factor: Real-time speed multiplier
        """
        # Header
        print("\n" + "✨" * self.emoji_width)
        print("🎉 Transcription Complete! 🎉")
        print("✨" * self.emoji_width)

        # Metrics
        print("\n" + "-" * 22)
        print("📝 [TIME REPORT]")
        metrics = [
            f"🔊 Audio Duration: {duration:.2f} seconds",
            f"⏱️ Total Processing: {total_time:.2f} seconds",
            f"✍️ Pure Transcription: {transcribe_time:.2f} seconds",
            f"🚀 Speed: {speed_factor:.2f}x real-time",
        ]

        for metric in metrics:
            print(metric)
        print("-" * 22)

    def log_delay_warning(self):
        """Display warning when transcription is delayed"""
        print("\n\n\nTranscription is taking longer than usual")
        print("⏳ Please be patient and DO NOT close the app\n\n")
