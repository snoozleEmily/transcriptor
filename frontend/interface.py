import sys
import tkinter as tk
from tkinter import ttk, filedialog
from queue import Empty, Queue


from .utils import open_browser
from .theme import configure_theme
from .constants import THEMES, FONTS, URLS
from .widgets.header import Header
from .widgets.buttons_panel import ButtonsPanel
from .async_processor import AsyncTaskManager



class Interface(tk.Tk):
    # --------------------- Console Log Set Up ---------------------
    class LogRedirector:
        def __init__(self, queue, widget):
            self.queue = queue
            self.widget = widget

        def write(self, text):
            self.queue.put(lambda: self._append_log(text))

        def _append_log(self, text):
            self.widget.config(state=tk.NORMAL)
            self.widget.insert(tk.END, text)
            self.widget.see(tk.END)
            self.widget.config(state=tk.DISABLED)

        def flush(self):
            pass

    # --------------------- Base Variables ---------------------
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

        # Redirect standard streams after UI is initialized
        sys.stdout = self.LogRedirector(self.gui_queue, self.log_text)
        sys.stderr = self.LogRedirector(self.gui_queue, self.log_text)

    # --------------------- Window Configuration ---------------------
    def _configure_window(self):
        """Establish main window properties"""
        self.title("Emily's Transcriptor")
        self.geometry("700x500")
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
            font=FONTS["emoji_small"],
            background=THEMES[self.current_theme]["bg"]
        )
        self.theme_emoji.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        self.theme_emoji.bind("<Button-1>", lambda e: self._toggle_theme())

    def _toggle_theme(self):
        """Handle theme toggle"""
        self.current_theme = "dark" if self.current_theme == "default" else "default"
        # Update theme emoji
        self.theme_emoji.config(
            text="🌙" if self.current_theme == "dark" else "☀️",
            background=THEMES[self.current_theme]["bg"]
        )
        # Update copy label colors
        self.copy_label.config(
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["fg"]
        )
        # Rest of existing theme configuration
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

# --------------------- Log display area ---------------------
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(expand=True, fill='both')

        # Console Log Title
        self.log_title = tk.Label(
            log_frame,
            text="Console Log",
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["fg"],
            font=FONTS["console"]
        )
        self.log_title.pack(side=tk.TOP, anchor="w", padx=5, pady=2)

        # Copy Button
        self.copy_label = tk.Label(
        log_frame,
        text="📋",
        bg=THEMES[self.current_theme]["bg"],
        fg=THEMES[self.current_theme]["fg"],
        font=FONTS["emoji_small"],
        cursor="hand2"
        )
        self.copy_label.place(relx=1.0, rely=0.0, anchor="ne", x=-1, y=1)
        self.copy_label.bind("<Button-1>", lambda e: self.copy_log())

        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            state='disabled',
            height=10,
            bg=THEMES[self.current_theme]['bg'],
            fg=THEMES[self.current_theme]['fg']
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def copy_log(self):
        """Copy log content to clipboard"""
        self.log_text.config(state=tk.NORMAL)
        text = self.log_text.get("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.show_feedback("Copied to clipboard!")

    def show_feedback(self, message):
        """Display temporary success message"""
        feedback_label = ttk.Label(
            self,
            text=message,
            foreground="green"
        )
        feedback_label.place(relx=0.5, rely=0.95, anchor="center")
        self.after(3000, feedback_label.destroy)

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
            self.async_mgr.get_busy(path)

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

    def show_error(self, message):
            """Display error message to user"""
            self.running = False
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