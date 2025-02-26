import tkinter as tk
from threading import Thread
from queue import Queue, Empty
from tkinter import ttk, filedialog, messagebox


from frontend.constants import COLOR_SCHEME, FONTS



class Interface(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.configure(bg=COLOR_SCHEME["bg"])
        self._setup_ui()
        self._configure_widgets()
        self.running = False
        self._alive = True
        self.gui_queue = Queue()
        self.protocol("WM_DELETE_WINDOW", self._safe_exit)
        self.after(100, self._process_gui_queue)

    def _setup_ui(self):
        self.title("Emily's Transcriptor")
        self.geometry("550x350")
        self.resizable(False, False)
        
        # Theme and color configuration
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TFrame", background=COLOR_SCHEME["bg"])
        style.configure("TLabel", background=COLOR_SCHEME["bg"], foreground=COLOR_SCHEME["fg"], font=FONTS["default"])
        style.configure("TButton",
                        background=COLOR_SCHEME["button_bg"],
                        foreground=COLOR_SCHEME["fg"],
                        font=FONTS["default"],
                        borderwidth=0)
        style.map("TButton",
                  background=[("active", COLOR_SCHEME["active_bg"])],
                  foreground=[("active", COLOR_SCHEME["active_fg"])])
        style.configure("TProgressbar", background=COLOR_SCHEME["progress_bg"], troughcolor=COLOR_SCHEME["trough"])

        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=40, pady=50)
        
        ttk.Label(main_frame, text="EMILY'S TRANSCRIPTOR", font=("Courier New", 16)).pack(pady=(0, 5))
        ttk.Label(main_frame, text="🎥", font=("Segoe UI Emoji", 64)).pack(pady=(0, 35))
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=(0, 15))
        
        self.select_button = ttk.Button(buttons_frame, text="SELECT VIDEO")
        self.github_button = ttk.Button(buttons_frame, text="GITHUB REPO")
        
        self.select_button.pack(side=tk.LEFT, padx=8)
        self.github_button.pack(side=tk.LEFT, padx=8)
        
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_label = ttk.Label(self.progress_frame, text="Ready")
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient='horizontal', length=300)
        
        self.progress_label.pack(pady=8)
        self.progress_bar.pack()

    def _configure_widgets(self):
        self.select_button.config(command=self._start_processing)
        self.github_button.config(command=self._open_github)

    def _start_processing(self):
        if self.running or not self._alive:
            return
            
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if path:
            self.running = True
            self.progress_frame.pack(pady=10)
            Thread(target=self._process_video, args=(path,), daemon=True).start()

    def _process_video(self, path):
        def queue_update(func):
            if self._alive:
                self.gui_queue.put(func)

        try:
            def update_progress(value: int, message: str):
                queue_update(lambda v=value, m=message: self._update_progress(v, m))
                
            self.controller.process_video(path, update_progress)
            queue_update(lambda: messagebox.showinfo("Success", "Transcription saved successfully!"))
            
        except Exception as e:
            error_msg = str(e)
            queue_update(lambda: messagebox.showerror("Error", error_msg))
            
        finally:
            queue_update(self._reset_progress)
            self.running = False

    def _process_gui_queue(self):
        while not self.gui_queue.empty():
            try:
                task = self.gui_queue.get_nowait()
                task()
            except Empty:
                break
        if self._alive:
            self.after(100, self._process_gui_queue)

    def _update_progress(self, value: int, message: str):
        if self._alive:
            self.progress_bar['value'] = value
            self.progress_label.config(text=message)

    def _reset_progress(self):
        if self._alive:
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Ready")
            self.progress_frame.pack_forget()

    def _open_github(self):
        if self._alive:
            import webbrowser
            webbrowser.open("https://github.com/snoozleEmily/transcriptor")

    def _safe_exit(self):
        self._alive = False
        self.gui_queue.queue.clear()
        self.destroy()