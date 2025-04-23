import time
import threading
from tqdm import tqdm
from typing import Optional, Callable

# Do I need this?
# Add this to prevent zombie threads
#def __del__(self):
#    self.active = False

class Loader:
    """Handles all progress tracking and visualization for transcription"""

    def __init__(self):
        self.active = False
        self.estimated_total = 0
        self.handler = None
        self.start_time = 0
        self.progress_bar = None
        self.delay_interval = 2.6

    def setup(
        self,
        setup_time: float,
        transcribe_estimate: float,
        handler: Optional[Callable] = None,
    ) -> None:
        """Initialize progress tracking with time estimates"""
        self.estimated_total = setup_time + transcribe_estimate
        self.handler = handler

    def show_setup_progress(self, setup_time: float) -> float:
        """Display model loading progress bar (returns start time)"""
        if setup_time <= 0:
            return time.time()

        with tqdm(
            total=setup_time,
            desc="Initializing Model",
            bar_format="\n{l_bar}| {n:.1f}/{total:.1f}s",
            unit="s",
        ) as bar:
            for _ in range(int(setup_time)):
                time.sleep(1)
                bar.update(1)

        return time.time()

    def start_transcription_progress(self, handler: Optional[Callable] = None) -> None:
        """Initialize and start transcription progress tracking"""
        self.progress_bar = tqdm(
            total=100,
            desc="\nTranscribing",
            bar_format="{l_bar}| {n:.0f}%",
            miniters=1,
            mininterval=0,
            maxinterval=1,
        )
        self.handler = handler
        self.start_time = time.time()
        self.active = True

        # Start monitoring threads
        self._start_progress_thread()
        self._start_watchdog()
        self._start_delay_indicator()

    def _start_progress_thread(self) -> None:
        """Thread for time-based progress updates"""

        def update():
            while self.active and self.progress_bar.n < 99:
                elapsed = time.time() - self.start_time
                progress = min((elapsed / self.estimated_total) * 100, 99)

                if progress > self.progress_bar.n:
                    self.update(progress - self.progress_bar.n)
                time.sleep(0.2)

        threading.Thread(target=update, daemon=True).start()

    def _start_watchdog(self) -> None:
        """Thread to force completion if stuck"""
        def watchdog():
            time.sleep(self.estimated_total + 1)
            if self.active and self.progress_bar.n < 100:
                self.update(100 - self.progress_bar.n)

        threading.Thread(target=watchdog, daemon=True).start()

    def _start_delay_indicator(self) -> None:
        """Thread for delay notifications (original behavior)"""

        def delay_indicator():
            while self.active and self.progress_bar.n > 99:
                time.sleep(0.1)

            if self.active and self.progress_bar.n > 100:
                print("\n\n⚠️ Transcription is taking longer than usual")
                print("⏳ Please be patient and DO NOT close the app\n\n")

            if self.active:
                with tqdm(
                    total=self.estimated_total,
                    desc="[DELAY] Still Transcribing",
                    bar_format="{l_bar} | Elapsed: {elapsed} seconds",
                    unit="s",
                    leave=False,
                ) as delay_bar:
                    while self.active:
                        time.sleep(self.delay_interval)
                        delay_bar.update(self.delay_interval)

        threading.Thread(target=delay_indicator, daemon=True).start()

    def update(self, progress: float) -> None:
        """Handle both absolute values and percentages"""
        if 0 <= progress <= 1:  # Convert fraction to percentage
            increment = (progress * 100) - self.progress_bar.n
            
        else:
            increment = progress - self.progress_bar.n
            
        if self.progress_bar:
            self.progress_bar.update(increment)

        if self.handler:
            self.handler(self.progress_bar.n)

    def complete(self, result: dict, duration: float) -> dict:
        """Finalize progress and add metadata"""
        if not self.progress_bar:
            return result

        self.progress_bar.update(100 - self.progress_bar.n)
        if self.handler:
            self.handler(100)

        transcribe_time = time.time() - self.start_time
        result["metadata"] = {
            "audio_duration": duration,
            "processing_time": time.time() - (self.start_time - self.estimated_total),
            "transcription_time": transcribe_time,
            "speed_factor": duration / transcribe_time if transcribe_time > 0 else 0,
        }

        self.active = False
        return result
