import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread



class TranscriptorApp(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()
        self._bind_events()

    def _setup_ui(self):
        """Configure visual elements"""
        self.title("Emily's Transcriptor")
        self.geometry("550x350")
        self.resizable(False, False)
        
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=40, pady=50)
        
        # Title
        title_label = ttk.Label(main_frame, text="EMILY'S TRANSCRIPTOR", font=("Courier New", 16))
        title_label.pack(pady=(0, 5))
        
        # Emoji
        emoji_label = ttk.Label(main_frame, text="🎥", font=("Segoe UI Emoji", 64))
        emoji_label.pack(pady=(0, 35))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=(0, 15))
        
        # Select video button
        self.select_button = ttk.Button(buttons_frame, text="SELECT VIDEO", command=self._start_processing)
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        # GitHub button
        self.github_button = ttk.Button(buttons_frame, text="GITHUB REPO", command=self._open_github)
        self.github_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_label = ttk.Label(self.progress_frame, text="Ready")
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient='horizontal', length=300)
        
        self.progress_label.pack(pady=5)
        self.progress_bar.pack()

    def _bind_events(self):
        """Configure event handlers"""
        self.select_button.config(command=self._start_processing)
        self.github_button.config(command=self._open_github)

    def _start_processing(self):
        """Initiate video processing thread"""
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if path:
            self.progress_frame.pack(pady=10)
            Thread(target=self._process_video, args=(path,), daemon=True).start()

    def _process_video(self, path):
        """Handle processing workflow"""
        try:
            def update_progress(value: int, message: str):
                self.progress_bar['value'] = value
                self.progress_label.config(text=message)
                self.update_idletasks()
                
            save_path = self.controller.process_video(path, update_progress)
            messagebox.showinfo("Success", f"Transcription saved to:\n{save_path}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Ready")
            self.progress_frame.pack_forget()

    def _open_github(self):
        """Open GitHub repository in browser"""
        import webbrowser
        webbrowser.open("https://github.com/snoozleEmily/transcriptor")
        messagebox.showinfo("GitHub", "Opening repository in your browser...")