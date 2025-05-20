# Deprecated

import time
import threading
from tqdm import tqdm
from typing import Optional, Callable


from src.utils.transcripting.info_dump import InfoDump



class Loader:
    """Handles progress visualization and timing for transcription pipeline"""
    def __init__(self):
        self.active: bool = False
        self.estimated_total: float = 0.0
        self.handler: Optional[Callable] = None
        self.start_time: float = 0.0
        self.progress_bar: Optional[tqdm] = None
        self.delay_interval: float = 2.6  # Seconds between delay updates

        self.info = InfoDump()

    def setup(
        self,
        setup_time: float,
        transcribe_estimate: float,
        handler: Optional[Callable] = None,
    ) -> None:
        """Initialize progress tracking parameters"""
        self.estimated_total = setup_time + transcribe_estimate
        self.handler = handler

    def show_setup_progress(self, setup_time: float) -> float:
        """Display model initialization progress bar"""
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
        """Initialize main transcription progress components"""
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

        self._start_progress_thread()
        self._start_watchdog()
        self._start_delay_indicator()

    def _start_progress_thread(self) -> None:
        """Time-based progress estimation thread"""
        def update():
            while self.active and self.progress_bar.n < 99:
                elapsed = time.time() - self.start_time
                progress = min((elapsed / self.estimated_total) * 100, 99)

                if progress > self.progress_bar.n:
                    self.update(progress - self.progress_bar.n)
                time.sleep(0.2)

        threading.Thread(target=update, daemon=True).start()

    def _start_watchdog(self) -> None:
        """Safety thread to force completion if stuck"""

        def watchdog():
            time.sleep(self.estimated_total + 1)
            if self.active and self.progress_bar.n < 100:
                self.update(100 - self.progress_bar.n)

        threading.Thread(target=watchdog, daemon=True).start()

    def _start_delay_indicator(self) -> None:
        """Delay notification system"""

        def delay_indicator():
            # Wait until transcription is "stuck" at high percentage
            while self.active and self.progress_bar.n < 99:
                time.sleep(0.1)

            # Show warning message once
            if self.active:
                self.info.log_delay_warning()

            # Show elapsed time progress
            with tqdm(
                total=self.estimated_total,
                desc="[DELAY] Still Transcribing",
                bar_format="{l_bar} | Elapsed: {elapsed}\n",
                unit="s",
                leave=False,  # Prevent residual progress bars
            ) as delay_bar:
                while self.active:
                    time.sleep(self.delay_interval)
                    delay_bar.update(self.delay_interval)
                    delay_bar.refresh()  # Prevent ANSI artifacts

        threading.Thread(target=delay_indicator, daemon=True).start()

    def update(self, increment: float) -> None:
        """Update progress with minimum 1% increments"""
        if self.progress_bar:
            current = self.progress_bar.n
            new_value = min(max(current + 1, current + increment), 100)
            self.progress_bar.update(new_value - current)

        if self.handler:
            self.handler(self.progress_bar.n if self.progress_bar else 0)

    def complete(self, result: dict, duration: float) -> dict:
        """Finalize progress tracking and cleanup"""
        self.active = False  # Signal threads to stop

        # Allow threads to exit gracefully
        time.sleep(0.4)

        if self.progress_bar:
            self.progress_bar.update(100 - self.progress_bar.n)
            self.progress_bar.close()
            self.progress_bar = None

        if self.handler:
            self.handler(100)

        # Add timing metadata
        if "metadata" not in result:
            result["metadata"] = {}

        result["metadata"].update(
            {
                "audio_duration": duration,
                "processing_time": time.time() - self.start_time,
                "speed_factor": (
                    duration / (time.time() - self.start_time)
                    if (time.time() - self.start_time) > 0
                    else 0
                ),
            }
        )

        return result
