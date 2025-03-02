import tkinter as tk
from threading import Thread
from queue import Queue, Empty
from tkinter import ttk, filedialog, messagebox


from .constants import COLOR_SCHEME, FONTS, URLS



class Interface(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.running = False
        self._alive = True
        self.gui_queue = Queue()
        
        # Initialize core application properties first
        self._configure_window()
        self._setup_theme()
        self._create_widgets()
        self._bind_actions()
        
        # Use safe shutdown handling for proper resource cleanup
        self.protocol("WM_DELETE_WINDOW", self._safe_exit)
        self.after(100, self._process_gui_queue)

    def _configure_window(self):
        """Set up main window properties that affect visual hierarchy"""
        self.title("Emily's Transcriptor")
        self.geometry("550x350")
        self.resizable(False, False)
        self.configure(bg=COLOR_SCHEME["bg"])

    def _setup_theme(self):
        """Configure visual styling to maintain consistent look across platforms"""
        style = ttk.Style(self)
        style.theme_use('clam')  # Provides most consistent baseline for customization
        
        # Unified styling ensures all components match the design system
        style.configure("TFrame", background=COLOR_SCHEME["bg"])
        style.configure("TLabel", 
                        background=COLOR_SCHEME["bg"], 
                        foreground=COLOR_SCHEME["fg"], 
                        font=FONTS["default"])
        style.configure("TButton",
                        background=COLOR_SCHEME["button_bg"],
                        foreground=COLOR_SCHEME["fg"],
                        font=FONTS["default"],
                        borderwidth=0)
        style.map("TButton",  # Interactive states help users understand button functionality
                 background=[("active", COLOR_SCHEME["active_bg"])],
                 foreground=[("active", COLOR_SCHEME["active_fg"])])

    def _create_widgets(self):
        """Build visual components with clear hierarchy and separation of concerns"""
        # Main container allows for consistent padding throughout UI
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=40, pady=50)
        
        # Title section establishes brand identity
        ttk.Label(main_frame, 
                 text="EMILY'S TRANSCRIPTOR", 
                 font=("Courier New", 16)).pack(pady=(0, 5))
        ttk.Label(main_frame, 
                 text="🎥", 
                 font=("Segoe UI Emoji", 64)).pack(pady=(0, 35))
        
        # Action buttons container maintains consistent spacing
        self.buttons_frame = ttk.Frame(main_frame)
        self.buttons_frame.pack(pady=(0, 15))
        
        # Primary interactive elements
        self.select_button = ttk.Button(self.buttons_frame, text="SELECT VIDEO")
        self.github_button = ttk.Button(self.buttons_frame, text="GITHUB REPO")
        
        # Button layout ensures proportional spacing
        self.select_button.pack(side=tk.LEFT, padx=8)
        self.github_button.pack(side=tk.LEFT, padx=8)

    def _bind_actions(self):
        """Connect user interactions to application logic"""
        self.select_button.config(command=self._start_processing)
        self.github_button.config(command=self._open_github)

    def _start_processing(self):
        """Handle video selection while preventing duplicate operations"""
        if self.running or not self._alive:
            return
            
        path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )
        if path:
            self.running = True
            Thread(target=self._process_video, args=(path,), daemon=True).start()

    def _process_video(self, path):
        """Coordinate video processing in background thread"""
        try:
            # Delegate processing to controller without UI updates
            self.controller.process_video(path)
            self.gui_queue.put(lambda: messagebox.showinfo(
                "Success", "Transcription saved successfully!"))
        except Exception as e:
            self.gui_queue.put(lambda e=e: messagebox.showerror("Error", str(e)))
        finally:
            self.running = False

    def _process_gui_queue(self):
        """Safely handle cross-thread GUI updates using message queue"""
        while not self.gui_queue.empty():
            try:
                task = self.gui_queue.get_nowait()
                task()
            except Empty:
                break
        if self._alive:
            self.after(100, self._process_gui_queue)

    def _open_github(self):
        """Provide quick access to project repository"""
        if self._alive:
            import webbrowser
            webbrowser.open(URLS)

    def _safe_exit(self):
        """Ensure clean shutdown and prevent zombie processes"""
        self._alive = False
        self.gui_queue.queue.clear()
        self.destroy()