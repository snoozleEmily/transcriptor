import tkinter as tk
from tkinter import ttk

from src.errors.debug import debug


class ButtonsPanel(ttk.Frame):
    """Interactive controls container with Pretty Notes option"""

    BUTTONS = ["SELECT VIDEO", "OPEN ISSUE", "ONLY TRANSCRIPTION", "ENABLE DEV LOGS"]

    def __init__(self, parent, select_handler, github_handler):
        super().__init__(parent)
        self.quick_script_fl = tk.BooleanVar(value=False)
        self.dev_logs_fl = tk.BooleanVar(value=False)
        self.dev_logs_fl.trace_add(  # Link checkbox to flag
            "write",  # for global-like usage throughout the code
            lambda *args: (
                debug.enable_dev_logs()
                if self.dev_logs_fl.get()
                else debug.disable_dev_logs()
            ),
        )
        self._create_widgets(select_handler, github_handler)

    def _create_widgets(self, select_handler, github_handler):
        style = ttk.Style()
        style.configure("OnlyScript.TCheckbutton", padding=5)
        style.configure("DevLogs.TCheckbutton", padding=5)

        # Create buttons and checkboxes
        self.select_btn = ttk.Button(self, text=self.BUTTONS[0], command=select_handler)
        self.github_btn = ttk.Button(self, text=self.BUTTONS[1], command=github_handler)
        self.quick_script_cb = ttk.Checkbutton(
            self,
            text=self.BUTTONS[2],
            variable=self.quick_script_fl,
            style="OnlyScript.TCheckbutton",
        )
        self.dev_logs_cb = ttk.Checkbutton(
            self,
            text=self.BUTTONS[3],
            variable=self.dev_logs_fl,
            style="DevLogs.TCheckbutton",
        )

        # --------------------- Layout ---------------------
        self.select_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.github_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.quick_script_cb.pack(side=tk.LEFT, padx=(0, 15))
        self.dev_logs_cb.pack(side=tk.LEFT, padx=(0, 15))

    def get_quick_script_flag(self):
        """Returns the current state of the Pretty Notes checkbox"""
        print(
            f"[DEBUG] self.quick_script_fl.get() returning in ButtonsPanel: {self.quick_script_fl.get()}"
        )
        return self.quick_script_fl.get()
