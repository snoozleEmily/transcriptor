import sys
import tkinter as tk
from tkinter import ttk, filedialog
from queue import Empty, Queue


from .url_opener import open_browser
from .theme import configure_theme
from .widgets.header import Header
from .widgets.buttons_panel import ButtonsPanel
from .async_processor import AsyncTaskManager
from .constants import THEMES, FONTS, GT_REPO

# TODO: Refactor this class into smaller modules


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
            self.gui_queue, self, self._complete_processing
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
        self.geometry("850x520")
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
        self.theme_emoji = tk.Label(
            self,
            text="🌙" if self.current_theme == "dark" else "☀️",
            font=FONTS["emoji_small"],
            background=THEMES[self.current_theme]["bg"],
            cursor="hand2",
        )
        self.theme_emoji.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        self.theme_emoji.bind("<Button-1>", lambda e: self._toggle_theme())

    def _toggle_theme(self):
        """Handle theme toggle"""
        self.current_theme = "dark" if self.current_theme == "default" else "default"
        self.theme_emoji.config(
            text="🌙" if self.current_theme == "dark" else "☀️",
            background=THEMES[self.current_theme]["bg"],
        )
        self.copy_label.config(
            bg=THEMES[self.current_theme]["bg"], fg=THEMES[self.current_theme]["fg"]
        )
        configure_theme(self, self.current_theme)
        self._update_root_theme()

    # --------------------- Layout Management ---------------------
    def _create_layout(self):
        """Build UI component hierarchy"""
        main_frame = ttk.Frame(self)
        main_frame.pack(
            expand=True, fill="both", 
            padx=40,  # height border
            pady=50   # width border
        )

        # Create top frame with 3 columns
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", pady=(0, 10))

        # Left panel for custom words
        words_frame = ttk.Frame(top_frame, width=150)
        words_frame.pack(side=tk.LEFT, fill="y", padx=(0, 10))
        self._create_custom_words_panel(words_frame)

        # Center header area -
        header_container = ttk.Frame(top_frame)
        header_container.pack(
            side=tk.LEFT,
            expand=True,  # this will expand to fill available space
            fill="both",
        )

        # Set branding (title and video emoji)
        header = Header(header_container)
        header.pack(expand=True, fill="both")

        # Right spacer
        right_spacer = ttk.Frame(top_frame, width=150)
        right_spacer.pack(side=tk.RIGHT, fill="y")

        # Buttons panel
        self.buttons_panel = ButtonsPanel(
            main_frame, self._start_processing, lambda: open_browser(GT_REPO)
        )
        self.buttons_panel.pack(pady=(0, 2))

        # Rest of the content
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True, fill="both")

        # --------------------- Console Log Setup ---------------------
        log_frame = ttk.Frame(content_frame)
        log_frame.pack(side=tk.LEFT, expand=True, fill="both", padx=(0, 10))

        # Console Log Title
        self.log_title = tk.Label(
            log_frame,
            text="Console Log",
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["fg"],
            font=FONTS["console"],
        )
        self.log_title.pack(side=tk.TOP, anchor="w", padx=0, pady=2)

        # Create the log text widget
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            state="disabled",
            height=1,
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["fg"],
            font=FONTS["console"],
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Copy Button
        self.copy_label = tk.Label(
            log_frame,
            text="📋",
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["fg"],
            font=FONTS["emoji_small"],
            cursor="hand2",
        )
        self.copy_label.place(relx=1.0, rely=0.0, anchor="ne", x=-1, y=-3)
        self.copy_label.bind("<Button-1>", lambda e: self.copy_log())

    # --------------------- Custom words panel methods ---------------------
    def _create_custom_words_panel(self, parent_frame):
        """Create compact custom words input panel"""
        # Frame for the title and toggle button
        title_frame = ttk.Frame(parent_frame)
        title_frame.pack(fill="x", pady=(0, 2))

        tk.Label(
            title_frame,
            text="Custom Terms",
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["fg"],
            font=FONTS["console"],
        ).pack(side=tk.LEFT, anchor="w")

        # Input area
        self.words_input_frame = ttk.Frame(parent_frame)
        self.words_input_frame.pack(fill="both", expand=True)

        # Compact text widget
        self.custom_words_text = tk.Text(
            self.words_input_frame,
            height=3,
            width=20,
            wrap=tk.WORD,
            font=FONTS["console"],
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["fg"],
            insertbackground=THEMES[self.current_theme]["fg"],
        )

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.words_input_frame, command=self.custom_words_text.yview
        )
        self.custom_words_text.configure(yscrollcommand=scrollbar.set)

        # Layout
        self.custom_words_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Initial text
        self.custom_words_text.insert(tk.END, "Enter words here")
        self.custom_words_text.bind("<FocusIn>", lambda e: self._clear_default_text())

    # --------------------- Helper Methods ---------------------
    def _clear_default_text(self):
        """Clear the default text when user clicks in the text widget"""
        if self.custom_words_text.get("1.0", "end-1c") == "Enter words here":
            self.custom_words_text.delete("1.0", tk.END)

    def copy_log(self):
        """Copy log content to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(self.log_text.get("1.0", tk.END))

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
        error_label = ttk.Label(self, text=f"Error: {message}", foreground="red")
        error_label.place(relx=0.5, rely=0.9, anchor="center")
        self.after(3000, error_label.destroy)

    def _safe_exit(self):
        """Ensure clean application termination"""
        self._alive = False
        self.gui_queue.queue.clear()
        self.destroy()
