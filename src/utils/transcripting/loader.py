import time
import threading
from typing import Optional, Callable


from .info_dump import InfoDump
from src.errors.exceptions import TranscriptionError



class Loader:
    """Handles real-time progress tracking for audio transcription processes."""
    def __init__(self):
        self.active = False  # Control flag for background threads
        self.handler = None  # Optional progress callback function
        self.start_time = 0.0  # Process start timestamp
        self.current_progress = 0  # 0-100 scale
        self.info = InfoDump()  # For logging system messages

        # Timing configuration
        self.estimated_total = 1.0  # Default 1s estimate to prevent division by zero
        self._MIN_SLEEP = 0.05  # Minimum sleep interval (50ms)
        self._SAFETY_BUFFER = 1.0  # Extra time before watchdog triggers

    def setup(self, setup_time: float, transcribe_estimate: float) -> None:
        """Configure time estimates for accurate progress tracking.

        Args:
            setup_time: Estimated initialization time in seconds
            transcribe_estimate: Expected transcription duration in seconds
        """
        self.estimated_total = max(0.1, transcribe_estimate)  # Prevent zero-division

    def show_setup_progress(self, setup_time: float) -> float:
        """Display and handle the initialization countdown.

        Returns:
            Timestamp when initialization completed
        """
        start = time.time()
        if setup_time <= 0:
            return start

        print(f"\nSystem initialization: {int(setup_time)}s estimated")
        for remaining in range(int(setup_time), 0, -1):
            print(f"Ready in {remaining}ss...\n", end="\r")
            time.sleep(1)

        print("Initialization complete\n")
        return time.time()

    def start_transcription_progress(
        self, handler: Optional[Callable[[int], None]] = None
    ) -> None:
        """Begin tracking transcription progress with dynamic updates."""
        self.handler = handler
        self.start_time = time.time()
        self.active = True
        self.current_progress = 0

        # Start monitoring threads
        threading.Thread(target=self._track_progress, daemon=True).start()
        threading.Thread(target=self._watch_for_delays, daemon=True).start()

    def _track_progress(self) -> None:
        """Main progress tracking logic with dynamic update intervals."""
        try:
            while self.active and self.current_progress < 100:
                elapsed = time.time() - self.start_time
                progress = min(99, (elapsed / self.estimated_total) * 100)

                if progress > self.current_progress:
                    self._update_display(progress - self.current_progress)

                # Calculate dynamic sleep time - faster updates near completion
                remaining_pct = (100 - progress) / 100
                sleep_time = max(self._MIN_SLEEP, 0.5 * remaining_pct)
                time.sleep(sleep_time)

            # Safety completion if we reach 100% naturally
            if self.current_progress >= 99 and self.active:
                self._update_display(100 - self.current_progress)
        
        except Exception as e:
            raise TranscriptionError.progress_tracking(error=e) from e


    def _watch_for_delays(self) -> None:
        """Monitor for processing delays and handle timeout cases."""
        # Wait until near completion or timeout
        time.sleep(self.estimated_total + self._SAFETY_BUFFER)

        if not self.active:
            return

        if self.current_progress < 100:
            # Start delay notification
            delay_start = time.time()
            self.info.log_delay_warning()

            # Show elapsed time since delay began
            while self.active:
                elapsed = int(time.time() - delay_start)
                print(f"Elapsed: {elapsed}ss || Still Transcripting\n", end="\r")
                time.sleep(1)

    def _update_display(self, increment: float) -> None:
        """Update progress display with thread-safe increments."""
        new_value = min(100, self.current_progress + max(1, int(increment)))
        if new_value > self.current_progress:
            self.current_progress = new_value
            print(f"Transcripting: {new_value}%\n", end="\r")

            if self.handler:
                self.handler(new_value)

    def complete(self, result: dict, duration: float) -> dict:
        """Finalize progress tracking and return processing metrics.

        Args:
            result: Dictionary to add metadata to
            duration: Original audio duration

        Returns:
            Result dict with added processing metadata
        """
        self.active = False
        time.sleep(0.1)  # Allow final updates to complete

        processing_time = time.time() - self.start_time
        self._update_display(100 - self.current_progress)

        result.setdefault("metadata", {}).update(
            {
                "audio_duration": duration,
                "processing_time": processing_time,
                "speed_factor": duration / processing_time,
            }
        )

        return result
