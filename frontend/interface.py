import tkinter as tk
from tkinter import ttk, filedialog
from queue import Empty, Queue


from .utils import open_browser
from .theme import configure_theme
from .constants import THEMES, URLS
from .widgets.header import Header
from .widgets.buttons_panel import ButtonsPanel
from .async_processor import AsyncTaskManager



class Interface(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.running = False
        self._alive = True
        self.current_theme = "default"
        self.gui_queue = Queue()
        self.async_mgr = AsyncTaskManager(
                    self.gui_queue,
                    self,
                    self._complete_processing
                )        
        

        # Initialization sequence
        self._configure_window()
        self._setup_theme()
        self._create_layout()
        self._create_theme_toggle()
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

    def _create_theme_toggle(self):
        """Create theme toggle emoji in top-right corner"""
        self.theme_emoji = ttk.Label(
            self,
            text="🌙" if self.current_theme == "dark" else "☀️",
            font=("Arial", 14),
            background=THEMES[self.current_theme]["bg"]
        )
        self.theme_emoji.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        self.theme_emoji.bind("<Button-1>", lambda e: self._toggle_theme())

    def _toggle_theme(self):
        """Handle theme toggle"""
        self.current_theme = "dark" if self.current_theme == "default" else "default"
        self.theme_emoji.config(
            text="🌙" if self.current_theme == "dark" else "☀️",
            background=THEMES[self.current_theme]["bg"]
        )
        configure_theme(self, self.current_theme)
        self._update_root_theme()

    # --------------------- Layout Management ---------------------
    def _create_layout(self):
        """Build UI component hierarchy"""
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both", padx=40, pady=50)

        Header(main_frame).pack()

        # Buttons panel
        self.buttons_panel = ButtonsPanel(
            main_frame,
            self._start_processing,
            lambda: open_browser(URLS)
        )
        self.buttons_panel.pack(pady=(0, 15))

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            main_frame,
            orient="horizontal",
            mode="determinate",
            length=400
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.pack_forget()  # Hide initially

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
            self.progress_bar.pack(pady=10)
            
            def update_progress(p):
                """Update progress bar from transcription logs"""
                self.progress_bar['value'] = p
                if p >= 100:
                    self.progress_bar.pack_forget()
                    
            self.async_mgr.get_busy(
                path,
                progress_handler=lambda p: self.gui_queue.put(
                    lambda: update_progress(p)
                )
            )

    def _complete_processing(self):
        """Cleanup after processing completes"""
        self.running = False
        self.gui_queue.put(lambda: self.progress_bar.pack_forget())

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

    def show_error(self, message):
            """Display error message to user"""
            self.running = False
            self.progress_bar.pack_forget()
            error_label = ttk.Label(
                self,
                text=f"Error: {message}",
                foreground="red"
            )
            error_label.place(relx=0.5, rely=0.9, anchor='center')
            self.after(3000, error_label.destroy)
            

    def _safe_exit(self):
        """Ensure clean application termination"""
        self._alive = False
        self.gui_queue.queue.clear()
        self.destroy()