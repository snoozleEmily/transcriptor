import tkinter as tk
from .constants import THEMES, FONTS

def create_branding(parent):
    """Build branding elements for the application"""
    container = tk.Frame(parent, bg=THEMES["bg"])
    
    # Application title
    tk.Label(
        container,
        text="EMILY'S TRANSCRIPTOR",
        font=FONTS["title"],
        bg=THEMES["bg"],
        fg=THEMES["fg"]
    ).pack(pady=(0, 5))

    # Emoji decoration
    tk.Label(
        container,
        text="🎥",
        font=FONTS["emoji"],
        bg=THEMES["bg"]
    ).pack(pady=(0, 35))
    
    return container