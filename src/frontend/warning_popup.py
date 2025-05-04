import tkinter as tk
from tkinter import ttk
from .constants import FONTS

class WarningPopup:
    WARNING_MSG = (
        "The Transcriptor is an experimental application in its early stage.\n"
        "This tool was made with the purpose of helping professionals optimize video "
        "training with specific targeted terms that common AIs do not have in their "
        "knowledge base. However, since it uses generative AI, the results might be wrong "
        "or incomplete. It's recommended to verify and confirm if they are as expected."
    )

    @staticmethod
    def show(parent, title="Warning", message=None, width=300):
        """Show a warning popup dialog"""
        popup = tk.Toplevel(parent)
        popup.title(title)
        popup.resizable(False, False)
        
        # Center the popup relative to parent
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 3)
        popup.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(popup, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning icon and message
        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            icon_frame,
            text="⚠️",
            font=FONTS["emoji_large"],
            foreground="orange"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Use class message if none provided
        display_message = message if message is not None else WarningPopup.WARNING_MSG
        
        tk.Label(
            icon_frame,
            text=display_message,
            font=FONTS["console"],
            justify=tk.LEFT,
            wraplength=width-50
        ).pack(side=tk.LEFT, fill=tk.X)
        
        # OK button
        ttk.Button(
            main_frame,
            text="I Understand",
            command=popup.destroy
        ).pack(pady=(10, 0))
        
        # Make modal
        popup.grab_set()
        popup.focus_force()
        parent.wait_window(popup)