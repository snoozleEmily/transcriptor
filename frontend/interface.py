# interface.py
import tkinter as tk
from tkinter import ttk, filedialog
from queue import Empty, Queue

from .theme import configure_theme
from .widgets.header import Header
from .widgets.buttons_panel import ButtonsPanel
from .async_processor import AsyncTaskManager
from .utils import open_browser
from .constants import THEMES, URLS



class Interface(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.running = False
        self._alive = True
        self.gui_queue = Queue()
        self.current_theme = "default"
        self.async_mgr = AsyncTaskManager(self.gui_queue)

        # Initialization sequence
        self._configure_window()
        self._setup_theme()
        self._create_layout()
        self._bind_cleanup()

    # --------------------- Window Configuration ---------------------
    def _configure_window(self):
        """Establish main window properties"""
        self.title("Emily's Transcriptor")
        self.geometry("550x350")
        self.resizable(False, False)
        self._update_root_theme()

    def _update_root_theme(self):
        """Update root window colors for current theme"""
        self.configure(bg=THEMES[self.current_theme]["bg"])

    # --------------------- Theme Management ---------------------
    def _setup_theme(self):
        """Initialize theme configuration"""
        configure_theme(self, self.current_theme)
        self._update_root_theme()

    def _toggle_theme(self):
        """Switch between available color themes"""
        self.current_theme = "dark" if self.current_theme == "default" else "default"
        configure_theme(self, self.current_theme)
        self._update_root_theme()
        self.update_idletasks()  # Force UI refresh

    # --------------------- Layout Management ---------------------
    def _create_layout(self):
        """Build UI component hierarchy"""
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=40, pady=50)

        Header(main_frame).pack()
        ButtonsPanel(
            main_frame,
            self._start_processing,
            lambda: open_browser(URLS),
            self._toggle_theme
        ).pack(pady=(0, 15))

    # --------------------- Core Functionality ---------------------
    def _start_processing(self):
        """Initiate video processing workflow"""
        if self.running or not self._alive:
            return

        path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )
        if path:
            self.running = True
            self.async_mgr.process_video(
                path,
                self.controller,
                self._complete_processing
            )

    def _complete_processing(self):
        """Cleanup after processing completes"""
        self.running = False

    # --------------------- System Operations ---------------------
    def _bind_cleanup(self):
        """Configure shutdown handlers"""
        self.protocol("WM_DELETE_WINDOW", self._safe_exit)
        self.after(100, self._monitor_gui_queue)

    def _monitor_gui_queue(self):
        """Handle cross-thread GUI updates"""
        while not self.gui_queue.empty():
            try:
                self.gui_queue.get_nowait()()
            except Empty:
                break
        if self._alive:
            self.after(100, self._monitor_gui_queue)

    def _safe_exit(self):
        """Ensure clean application termination"""
        self._alive = False
        self.gui_queue.queue.clear()
        self.destroy()