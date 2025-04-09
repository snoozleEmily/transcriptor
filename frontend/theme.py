from tkinter import ttk
from .constants import THEMES, FONTS



def configure_theme(root, theme_name="default"):
    """Configures ttk styles for a given theme"""
    style = ttk.Style(root)
    style.theme_use('clam')
    colors = THEMES[theme_name]

    # Base styles
    style.configure(
        "TFrame",
        background=colors["bg"]
    )
    style.configure(
        "TLabel",
        background=colors["bg"],
        foreground=colors["fg"],
        font=FONTS["default"]
    )
    style.configure(
        "TButton",
        background=colors["button_bg"],
        foreground=colors["fg"],
        font=FONTS["default"],
        borderwidth=0
    )
    
    # Interactive states
    style.map(
        "TButton",
        background=[("active", colors["active_bg"])],
        foreground=[("active", colors["active_fg"])]
    )

    # Custom widget styles
    style.configure(
        "HeaderTitle.TLabel",
        font=FONTS["title"]
    )
    style.configure(
        "EmojiDisplay.TLabel",
        font=FONTS["emoji"]
    )