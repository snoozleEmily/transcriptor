import threading
import webbrowser
from tkinter import messagebox, filedialog

from .views import MainWindow
from frontend import constants
from utils.transcriber import Transcriber
from utils.file_handler import save_transcription
from utils.audio_processor import check_ffmpeg, extract_audio
from errors.handlers import catch_errors, format_error



class TranscriptorController:
    """Handles application business logic and workflow"""
    def __init__(self, root):
        self.root = root
        self.view = MainWindow(root)
        self.progress_active = False
        self.transcriber = Transcriber(model_size="tiny")
        
        # Connect UI actions
        self.view.select_button.config(command=self.handle_video_selection)
        self.view.github_button.config(command=self.open_github_repo)

    @catch_errors
    def handle_video_selection(self):
        if self.progress_active:
            messagebox.showinfo("Already Running", "A video is already being processed!")
            return

        if file_path := filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        ):
            self.progress_active = True
            self.view.show_progress()
            threading.Thread(target=self.process_video, args=(file_path,), daemon=True).start()

    def update_progress(self, value):
        self.view.update_progress(value)
        self.root.update_idletasks()

    def process_video(self, video_path):
        """Handle full video processing pipeline"""
        try:
            # Audio extraction (30% progress)
            self.update_progress(10)
            check_ffmpeg()
            self.update_progress(30)
            audio_path = extract_audio(video_path)
            
            # Transcription (60% progress)
            self.update_progress(50)
            transcription = self.transcriber.transcribe(audio_path)
            self.update_progress(80)
            
            # Save results
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )
            if save_path:
                save_transcription(transcription, save_path)
                self.update_progress(100)
                messagebox.showinfo("Success", "Transcription saved successfully!")
        
        except Exception as e:
            error_info = format_error(e)
            messagebox.showerror(
                f"Error {error_info['code']}",
                error_info['message']
            )
        finally:
            self.progress_active = False
            self.view.hide_progress()

    def open_github_repo(self):
        webbrowser.open(constants.URLS["github_repo"])
        messagebox.showinfo("GitHub Repo", "Opening repository in your browser...")