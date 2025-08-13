import sys
import tkinter as tk
from tkinter import ttk, filedialog
from queue import Empty, Queue


from .url_opener import open_browser
from .theme import configure_theme
from .widgets.header import Header
from .warning_popup import WarningPopup
from .widgets.buttons_panel import ButtonsPanel
from .async_processor import AsyncTaskManager
from src.utils.text.content_type import ContentType
from .constants import THEMES, PLACEHOLDER_TEXT, FONTS, BUG_REPORTS_GT


# TODO: Refactor this class into smaller modules?


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

        # Message for Custom Words
        self.C_WORDS_EX = f"Enter words here!\n\nTell transcriptor which custom words to look out for in the video.\n"

        # Initialization sequence
        self._configure_window()
        self._setup_theme()
        self._create_layout()
        self._create_theme_toggle()
        self._bind_cleanup()

        # Redirect standard streams after UI is initialized
        sys.stdout = self.LogRedirector(self.gui_queue, self.log_text)
        sys.stderr = self.LogRedirector(self.gui_queue, self.log_text)

        self.after(100, lambda: WarningPopup.show(self, title="Important Notice"))

    # --------------------- Window Configuration ---------------------
    def _configure_window(self):
        """Establish main window properties"""
        self.title("Emily's Transcriptor")
        self.geometry("850x530")
        self.resizable(False, False)
        self._update_root_theme()

        # Bring to front on startup
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes, "-topmost", False)

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
        main_frame.pack(expand=True, fill="both", padx=40, pady=50)

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
            main_frame, self._start_processing, lambda: open_browser(BUG_REPORTS_GT)
        )
        self.buttons_panel.pack(pady=(0, 2))

        # Rest of the content
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True, fill="both")

        # --------------------- Console Log Setup ---------------------
        self.log_frame = ttk.Frame(content_frame)
        self.log_frame.pack(side=tk.LEFT, expand=True, fill="both", padx=(0, 10))

        # Console Log Title
        self.log_title = tk.Label(
            self.log_frame,
            text="Console Log",
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["fg"],
            font=FONTS["console"],
        )
        self.log_title.pack(side=tk.TOP, anchor="w", padx=0, pady=2)

        # Create the log text widget
        self.log_text = tk.Text(
            self.log_frame,
            wrap=tk.WORD,
            state="disabled",
            height=1,
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["fg"],
            font=FONTS["console"],
        )
        scrollbar = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Copy Button
        self.copy_label = tk.Label(
            self.log_frame,
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
            text="Custom Words",
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["fg"],
            font=FONTS["console"],
        ).pack(side=tk.LEFT, anchor="w")

        # Input area
        self.words_input_frame = ttk.Frame(parent_frame)
        self.words_input_frame.pack(fill="both", expand=True)

        # Compact text widget
        self.custom_words_raw = tk.Text(
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
            self.words_input_frame, command=self.custom_words_raw.yview
        )
        self.custom_words_raw.configure(yscrollcommand=scrollbar.set)

        # Layout
        self.custom_words_raw.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Track if user has modified the content
        self.custom_words_modified = False

        # Initial text
        self._show_placeholder_text()

        # Implement focus events
        self.custom_words_raw.bind("<FocusIn>", lambda e: self._on_focus_in())
        self.custom_words_raw.bind("<FocusOut>", lambda e: self._on_focus_out())
        self.custom_words_raw.bind("<Key>", lambda e: self._on_key_press())

    def _show_placeholder_text(self):
        """Show the placeholder text"""
        self.custom_words_raw.insert(tk.END, self.C_WORDS_EX)
        self.custom_words_raw.config(fg=PLACEHOLDER_TEXT)
        self.custom_words_modified = False

    def _on_focus_in(self):
        """Handle focus in event"""
        if not self.custom_words_modified:
            self.custom_words_raw.delete("1.0", tk.END)
            self.custom_words_raw.config(fg=THEMES[self.current_theme]["fg"])

    def _on_focus_out(self):
        """Handle focus out event"""
        if not self.custom_words_modified and not self.custom_words_raw.get(
            "1.0", "end-1c"
        ):
            self._show_placeholder_text()

    def _on_key_press(self):
        """Handle key press event - mark as modified"""
        if not self.custom_words_modified:
            self.custom_words_modified = True
            current_text = self.custom_words_raw.get("1.0", "end-1c")

            # If user pressed a key but then deleted everything,
            # we should still consider it modified
            if not current_text:
                self.custom_words_modified = True

    # --------------------- Helper Methods ---------------------
    def _clear_default_text(self):
        """Clear the default text when user clicks in the text widget"""
        if self.custom_words_raw.get("1.0", "end-1c") == self.C_WORDS_EX:
            self.custom_words_raw.delete("1.0", tk.END)

    def copy_log(self):
        """Copy log content to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(self.log_text.get("1.0", tk.END))
        self.log_text.config(state=tk.NORMAL)
        text = self.log_text.get("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.show_feedback("✓ Copied to clipboard!")

    def show_feedback(self, message):
        """Display temporary success message"""
        feedback_label = ttk.Label(
            self, text=message, foreground=THEMES[self.current_theme]["message"]
        )
        feedback_label.place(relx=0.5, rely=0.95, anchor="center")

        # Remove the notification after 2 seconds
        self.after(2000, feedback_label.destroy)

    # --------------------- Core Functionality ---------------------
    def _start_processing(self):
        """Initiate video processing workflow"""
        if self.running or not self._alive:
            return

        path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )
        if path:
            # Get format preference before processing
            quick_script = self.buttons_panel.get_quick_script_flag()

            # Get custom words from the text console and process them
            custom_words_raw = self.custom_words_raw.get("1.0", tk.END).strip()
            custom_words = None

            # Only process if user entered actual words (not the example text)
            if custom_words_raw and custom_words_raw != self.C_WORDS_EX:
                # Split by commas or newlines, strip whitespace, remove empty entries
                word_list = [
                    word.strip()
                    for word in custom_words_raw.replace("\n", ",").split(",")
                    if word.strip()
                ]
                # Dynamically extract all lines from the placeholder text
                placeholders = [
                    line.strip()
                    for line in self.C_WORDS_EX.splitlines()
                    if line.strip()
                ]
                filtered_words = [w for w in word_list if w not in placeholders]
                custom_words = {word: [] for word in filtered_words}
                has_odd = bool(custom_words)

            else:
                custom_words = None
                has_odd = False

            config = ContentType(
                words=custom_words,
                has_odd_names=has_odd,
                has_code=False,
                types=[],
                is_multilingual=False,
            )

            self.running = True
            self.async_mgr.get_busy(
                path, config_params=config, quick_script=quick_script
            )

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

    # --------------------- Async Completion Handler ---------------------
    def _complete_processing(self):
        """Handle completion of async processing"""
        self.running = False
        self.show_feedback("✓ Processing complete!")
        """Handle completion of async processing"""
        self.running = False
        self.show_feedback("✓ Processing complete!")
