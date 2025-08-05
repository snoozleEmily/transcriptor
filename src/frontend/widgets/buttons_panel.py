import tkinter as tk
from tkinter import ttk


class ButtonsPanel(ttk.Frame):
    """Interactive controls container with Pretty Notes option"""

    BUTTONS = ["SELECT VIDEO", "PRETTY NOTES", "OPEN ISSUE"]

    def __init__(self, parent, select_handler, github_handler):
        super().__init__(parent)
        self.pretty_notes_fl = tk.BooleanVar(value=False)
        self._create_widgets(select_handler, github_handler)

    def _create_widgets(self, select_handler, github_handler):
        style = ttk.Style()
        style.configure("PrettyNotes.TCheckbutton", font=("Courier New", 10), padding=5)

        # Create buttons and checkbox
        self.select_btn = ttk.Button(self, text=self.BUTTONS[0], command=select_handler)

        self.pretty_notes_cb = ttk.Checkbutton(
            self,
            text=self.BUTTONS[1],
            variable=self.pretty_notes_fl,
            style="PrettyNotes.TCheckbutton",
        )

        self.github_btn = ttk.Button(self, text=self.BUTTONS[2], command=github_handler)

        # --------------------- Layout ---------------------
        self.select_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.pretty_notes_cb.pack(side=tk.LEFT, padx=(0, 15))
        self.github_btn.pack(side=tk.LEFT, padx=(0, 15))

    def get_pretty_notes_flag(self):
        """Returns the current state of the Pretty Notes checkbox"""
        return self.pretty_notes_fl.get()
        return self.pretty_notes_fl.get()
