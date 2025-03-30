import tkinter as tk
from tkinter import ttk



class ProgressHandler:
    """Handles progress tracking components and their behavior"""
    def __init__(self, parent, theme):
        """Create progress tracking components"""
        self.frame = tk.Frame(parent, bg=theme["bg"])
        self.theme = theme
        
        self.progress_label = ttk.Label(self.frame, text="Processing: 0%")
        self.progress_bar = ttk.Progressbar(
            self.frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate'
        )
        
        self.progress_label.pack(pady=5)
        self.progress_bar.pack()

    def show(self):
        """Display progress indicators"""
        self.frame.pack(pady=10)

    def hide(self):
        """Remove progress indicators from view"""
        self.frame.pack_forget()

    def update(self, value):
        """Update progress visualization"""
        self.progress_bar['value'] = value
        self.progress_label.config(text=f"Processing: {value}%")

    def show_message(self, message):
        """Display dynamic processing messages"""
        self.progress_label.config(text=message)