from tkinter import ttk
from .constants import THEMES, FONTS

class StyleManager:
    """Handles all visual styling standards for the application"""
    def __init__(self):
        self.style = ttk.Style()
        
    def configure_styles(self):
        """Establish all visual styling standards"""
        self.style.theme_use('alt')
        self._configure_label_style()
        self._configure_button_style()
        self._configure_progress_style()

    def _configure_label_style(self):
        """Configure label styling standards"""
        self.style.configure(
            'TLabel',
            background=THEMES["bg"],
            foreground=THEMES["fg"],
            font=FONTS["default"]
        )

    def _configure_button_style(self):
        """Configure button styling standards"""
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

    def _configure_progress_style(self):
        """Configure progress bar styling standards"""
        self.style.configure(
            "Horizontal.TProgressbar",
            background=THEMES["progress_bg"],
            troughcolor=THEMES["trough"],
            thickness=10
        )