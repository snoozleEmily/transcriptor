# widgets/buttons_panel.py
import tkinter as tk
from tkinter import ttk

class ButtonsPanel(ttk.Frame):
    """Interactive controls container"""
    def __init__(self, parent, select_handler, github_handler):
        super().__init__(parent)
        self._create_widgets(select_handler, github_handler)
        self.buttons = {}

    def _create_widgets(self, select_handler, github_handler):
        self.select_btn = ttk.Button(
            self,
            text="SELECT VIDEO",
            command=select_handler
        )
        self.github_btn = ttk.Button(
            self,
            text="GITHUB REPO",
            command=github_handler
        )
        
        self.select_btn.pack(side=tk.LEFT, padx=8)
        self.github_btn.pack(side=tk.LEFT, padx=8)