import tkinter as tk
from tkinter import ttk



class ButtonsPanel(ttk.Frame):
    """Interactive controls container"""
    def __init__(self, parent, select_handler, github_handler, theme_handler):
        super().__init__(parent)
        self.frame = ttk.Frame(parent)
        self._create_widgets(select_handler, github_handler, theme_handler)
        self.buttons = {}

    def _create_widgets(self, select_handler, github_handler, theme_handler):
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
        self.theme_btn = ttk.Button(
            self,
            text="TOGGLE THEME",
            command=theme_handler
        )
        
        self.select_btn.pack(side=tk.LEFT, padx=8)
        self.github_btn.pack(side=tk.LEFT, padx=8)
        self.theme_btn.pack(side=tk.LEFT, padx=8)

    def add_button(self, name, text, command=None):
        """Add a new button to the panel"""
        self.buttons[name] = ttk.Button(
            self.frame,
            text=text,
            command=command
        )
        self.buttons[name].pack(side='left', padx=5)
        
    def get_button(self, name):
        """Retrieve a button by name"""
        return self.buttons.get(name)