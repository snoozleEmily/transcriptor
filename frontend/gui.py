import tkinter as tk
from queue import Empty, Queue
from threading import Thread
from tkinter import filedialog, messagebox, ttk


from .constants import COLOR_SCHEME, FONTS, URLS



class Interface(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.running = False
        self._alive = True
        self.gui_queue = Queue()

        # Initialization sequence
        self._configure_window()
        self._setup_theme()
        self._create_widgets()
        self._bind_actions()

        # System setup
        self.protocol("WM_DELETE_WINDOW", self._safe_exit)
        self.after(100, self._process_gui_queue)

    # --------------------- Window Configuration ---------------------
    def _configure_window(self):
        """Establish main window properties"""
        self.title("Emily's Transcriptor")
        self.geometry("550x350")
        self.resizable(False, False)
        self.configure(bg=COLOR_SCHEME["bg"])

    def _setup_theme(self):
        """Configure visual theme and component styling"""
        style = ttk.Style(self)
        style.theme_use('clam')

        # Base styling
        style.configure(
            "TFrame",
            background=COLOR_SCHEME["bg"]
        )
        style.configure(
            "TLabel",
            background=COLOR_SCHEME["bg"],
            foreground=COLOR_SCHEME["fg"],
            font=FONTS["default"]
        )
        style.configure(
            "TButton",
            background=COLOR_SCHEME["button_bg"],
            foreground=COLOR_SCHEME["fg"],
            font=FONTS["default"],
            borderwidth=0
        )
        
        # Interactive states
        style.map(
            "TButton",
            background=[("active", COLOR_SCHEME["active_bg"])],
            foreground=[("active", COLOR_SCHEME["active_fg"])]
        )

    # --------------------- Widget Construction ---------------------
    def _create_widgets(self):
        """Build UI component hierarchy"""
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=40, pady=50)

        # Branding elements
        ttk.Label(
            main_frame,
            text="EMILY'S TRANSCRIPTOR",
            font=("Courier New", 16)
        ).pack(pady=(0, 5))
        
        ttk.Label(
            main_frame,
            text="🎥",
            font=("Segoe UI Emoji", 64)
        ).pack(pady=(0, 35))

        # Interactive controls
        self.buttons_frame = ttk.Frame(main_frame)
        self.buttons_frame.pack(pady=(0, 15))

        self.select_button = ttk.Button(
            self.buttons_frame,
            text="SELECT VIDEO"
        )
        self.github_button = ttk.Button(
            self.buttons_frame,
            text="GITHUB REPO"
        )

        self.select_button.pack(side=tk.LEFT, padx=8)
        self.github_button.pack(side=tk.LEFT, padx=8)

    # --------------------- Event Handling ---------------------
    def _bind_actions(self):
        """Connect UI elements to functionality"""
        self.select_button.config(command=self._start_processing)
        self.github_button.config(command=self._open_github)

    def _start_processing(self):
        """Initiate video processing workflow"""
        if self.running or not self._alive:
            return

        path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )
        if path:
            self.running = True
            Thread(
                target=self._process_video,
                args=(path,),
                daemon=True
            ).start()

    def _process_video(self, path):
        """Execute video processing in background thread"""
        try:
            self.controller.process_video(path)
            self.gui_queue.put(lambda: messagebox.showinfo(
                "Success", 
                "Transcription saved successfully!"
            ))
        except Exception as e:
            self.gui_queue.put(lambda e=e: messagebox.showerror(
                "Error", 
                str(e)
            ))
        finally:
            self.running = False

    def _process_gui_queue(self):
        """Handle cross-thread GUI updates"""
        while not self.gui_queue.empty():
            try:
                task = self.gui_queue.get_nowait()
                task()
            except Empty:
                break
        if self._alive:
            self.after(100, self._process_gui_queue)

    # --------------------- System Operations ---------------------
    def _open_github(self):
        """Launch project repository in browser"""
        if self._alive:
            import webbrowser
            webbrowser.open(URLS)

    def _safe_exit(self):
        """Ensure clean application termination"""
        self._alive = False
        self.gui_queue.queue.clear()
        self.destroy()