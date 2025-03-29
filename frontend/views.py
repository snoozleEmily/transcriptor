import tkinter as tk
from tkinter import ttk


from .constants import THEMES, FONTS



class MainWindow:
    """Handles GUI setup and visual components"""
    def __init__(self, root):
        self.root = root
        self._initialize_components()

    def _initialize_components(self):
        """Core initialization sequence"""
        self.configure_root()
        self.setup_styles()
        self.create_widgets()

    # --------------------- Window Configuration ---------------------
    def configure_root(self):
        """Configure main window properties"""
        self.root.title("Emily's Transcriptor")
        self.root.geometry("550x350")
        self.root.configure(bg=THEMES["bg"])
        self.root.resizable(False, False)

    def setup_styles(self):
        """Establish visual styling standards"""
        self.style = ttk.Style()
        self.style.theme_use('alt')

        self.style.configure(
            'TLabel',
            background=THEMES["bg"],
            foreground=THEMES["fg"],
            font=FONTS["default"]
        )
        
        self.style.configure(
            'TButton',
            background=THEMES["button_bg"],
            foreground=THEMES["fg"],
            borderwidth=0,
            font=FONTS["default"],
            width=20
        )
        
        self.style.map(
            'TButton',
            background=[('active', THEMES["active_bg"])],
            foreground=[('active', THEMES["active_fg"])]
        )

        self.style.configure(
            "Horizontal.TProgressbar",
            background=THEMES["progress_bg"],
            troughcolor=THEMES["trough"],
            thickness=10
        )

    # --------------------- Widget Construction ---------------------
    def create_widgets(self):
        """Build primary interface components"""
        self.main_frame = tk.Frame(self.root, bg=THEMES["bg"])
        self.main_frame.pack(expand=True, fill='both', padx=40, pady=50)

        # Branding elements
        tk.Label(
            self.main_frame,
            text="EMILY'S TRANSCRIPTOR",
            font=FONTS["title"],
            bg=THEMES["bg"],
            fg=THEMES["fg"]
        ).pack(pady=(0, 5))

        tk.Label(
            self.main_frame,
            text="🎥",
            font=FONTS["emoji"],
            bg=THEMES["bg"]
        ).pack(pady=(0, 35))

        # Interactive controls
        self.buttons_frame = tk.Frame(
            self.main_frame,
            bg=THEMES["bg"]
        )
        self.buttons_frame.pack(pady=(0, 15))
        
        self.select_button = ttk.Button(
            self.buttons_frame,
            text="SELECT VIDEO"
        )
        self.github_button = ttk.Button(
            self.buttons_frame,
            text="GITHUB REPO"
        )
        self.select_button.pack(side=tk.LEFT, padx=5)
        self.github_button.pack(side=tk.LEFT, padx=5)

        # Progress system
        self._build_progress_indicator()

    def _build_progress_indicator(self):
        """Create progress tracking components"""
        self.progress_frame = tk.Frame(
            self.main_frame,
            bg=THEMES["bg"]
        )
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="Processing: 0%"
        )
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate'
        )
        self.progress_label.pack(pady=5)
        self.progress_bar.pack()

    # --------------------- Progress Management ---------------------
    def show_progress(self):
        """Display progress indicators"""
        self.progress_frame.pack(pady=10)

    def hide_progress(self):
        """Remove progress indicators from view"""
        self.progress_frame.pack_forget()

    def update_progress(self, value):
        """Update progress visualization"""
        self.progress_bar['value'] = value
        self.progress_label.config(text=f"Processing: {value}%")

    def show_processing_state(self, message):
        """Display dynamic processing messages"""
        self.progress_label.config(text=message)
        self.root.update_idletasks()