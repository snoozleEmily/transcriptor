import tkinter as tk
from tkinter import ttk

import constants


class MainWindow:
    """Handles GUI setup and visual components"""
    def __init__(self, root):
        self.root = root
        self.configure_root()
        self.setup_styles()
        self.create_widgets()

    def configure_root(self):
        self.root.title("Emily's Transcriptor")
        self.root.geometry("550x350")
        self.root.configure(bg=constants.COLOR_SCHEME["bg"])
        self.root.resizable(False, False)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('alt')
        
        self.style.configure('TLabel', 
                           background=constants.COLOR_SCHEME["bg"], 
                           foreground=constants.COLOR_SCHEME["fg"],
                           font=constants.FONTS["default"])
        
        self.style.configure('TButton', 
                           background=constants.COLOR_SCHEME["button_bg"],
                           foreground=constants.COLOR_SCHEME["fg"],
                           borderwidth=0,
                           font=constants.FONTS["default"],
                           width=20)
        
        self.style.map('TButton', 
                     background=[('active', constants.COLOR_SCHEME["active_bg"])],
                     foreground=[('active', constants.COLOR_SCHEME["active_fg"])])

        self.style.configure("Horizontal.TProgressbar",
                           background=constants.COLOR_SCHEME["progress_bg"],
                           troughcolor=constants.COLOR_SCHEME["trough"],
                           thickness=10)

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg=constants.COLOR_SCHEME["bg"])
        self.main_frame.pack(expand=True, fill='both', padx=40, pady=50)

        # Title components
        tk.Label(self.main_frame,
                text="EMILY'S TRANSCRIPTOR",
                font=constants.FONTS["title"],
                bg=constants.COLOR_SCHEME["bg"],
                fg=constants.COLOR_SCHEME["fg"]).pack(pady=(0, 5))

        tk.Label(self.main_frame,
                text="🎥",
                font=constants.FONTS["emoji"],
                bg=constants.COLOR_SCHEME["bg"]).pack(pady=(0, 35))

        # Action buttons
        self.buttons_frame = tk.Frame(self.main_frame, bg=constants.COLOR_SCHEME["bg"])
        self.buttons_frame.pack(pady=(0, 15))
        
        self.select_button = ttk.Button(self.buttons_frame, text="SELECT VIDEO")
        self.github_button = ttk.Button(self.buttons_frame, text="GITHUB REPO")
        self.select_button.pack(side=tk.LEFT, padx=5)
        self.github_button.pack(side=tk.LEFT, padx=5)

        # Progress indicator
        self.progress_frame = tk.Frame(self.main_frame, bg=constants.COLOR_SCHEME["bg"])
        self.progress_label = ttk.Label(self.progress_frame, text="Processing: 0%")
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                          orient=tk.HORIZONTAL,
                                          length=300,
                                          mode='determinate')
        self.progress_label.pack(pady=5)
        self.progress_bar.pack()

    def show_progress(self):
        self.progress_frame.pack(pady=10)

    def hide_progress(self):
        self.progress_frame.pack_forget()

    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.progress_label.config(text=f"Processing: {value}%")

    def show_processing_state(self, message):
        self.progress_label.config(text=message)
        self.root.update_idletasks()