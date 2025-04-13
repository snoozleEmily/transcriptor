import tkinter as tk


from ..styles_manager import StyleManager
from ..constants import THEMES
from .branding import create_branding
from .buttons_panel import ButtonsPanel



class MainWindow:
    """Handles GUI setup and visual components"""
    def __init__(self, root):
        """Initialize main application window"""
        self.root = root
        self.style_manager = StyleManager()
        self._initialize_components()

    def _initialize_components(self):
        """Core initialization sequence"""
        self._configure_root()
        self.style_manager.configure_styles()
        self._create_interface()

    def _configure_root(self):
        """Configure main window properties"""
        self.root.title("Emily's Transcriptor")
        self.root.geometry("550x350")
        self.root.configure(bg=THEMES["bg"])
        self.root.resizable(False, False)

    def _create_interface(self):
        """Build primary interface components"""
        self.main_frame = tk.Frame(self.root, bg=THEMES["bg"])
        self.main_frame.pack(expand=True, fill='both', padx=40, pady=50)

        # Branding elements
        create_branding(self.main_frame).pack()

        # Interactive controls
        self.button_panel = ButtonsPanel(self.main_frame)
        self.button_panel.add_button('select', "SELECT VIDEO")
        self.button_panel.add_button('github', "GITHUB REPO")
        self.button_panel.frame.pack(pady=(0, 15))

        # Progress system
        # Show progress bar and status label here