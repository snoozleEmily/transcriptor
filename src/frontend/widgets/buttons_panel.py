import tkinter as tk
from tkinter import ttk


class ButtonsPanel(ttk.Frame):
    """Interactive controls container with Pretty Notes option"""

    BUTTONS = ["SELECT VIDEO", "OPEN ISSUE", "ONLY TRANSCRIPTION"]

    def __init__(self, parent, select_handler, github_handler):
        super().__init__(parent)
        self.quick_script_fl = tk.BooleanVar(value=False)
        self._create_widgets(select_handler, github_handler)

    def _create_widgets(self, select_handler, github_handler):
        style = ttk.Style()
        style.configure("OnlyScript.TCheckbutton", font=("Courier New", 10), padding=5)

        # Create buttons and checkbox
        self.select_btn = ttk.Button(self, text=self.BUTTONS[0], command=select_handler)

        self.github_btn = ttk.Button(self, text=self.BUTTONS[1], command=github_handler)

        self.quick_script_cb = ttk.Checkbutton(
            self,
            text=self.BUTTONS[2],
            variable=self.quick_script_fl,
            style="OnlyScript.TCheckbutton",
        )

        # --------------------- Layout ---------------------
        self.select_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.github_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.quick_script_cb.pack(side=tk.LEFT, padx=(0, 15))

    def get_quick_script_flag(self):
        """Returns the current state of the Pretty Notes checkbox"""
        print(
            f"[DEBUG] self.quick_script_fl.get() returning in ButtonsPanel: {self.quick_script_fl.get()}"
        )
        return self.quick_script_fl.get()
