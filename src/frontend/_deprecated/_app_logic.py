import threading
import webbrowser
from tkinter import messagebox, filedialog


from frontend import constants
from ..widgets.window import MainWindow
from utils.transcriber import Textify
from utils.file_handler import save_transcription
from utils.audio_processor import check_ffmpeg, extract_audio
from errors.handlers import catch_errors, format_error



class TranscriptorController:
    """Handles application business logic and workflow"""
    def __init__(self, root):
        self.root = root
        self.view = MainWindow(root)
        self.transcriber = Textify(model_size="tiny")
        self.processing_active = False

        # Initialize UI bindings
        self._setup_connections()

    # --------------------- Initialization ---------------------
    def _setup_connections(self):
        """Connect UI elements to controller methods"""
        self.view.select_button.config(command=self.handle_video_selection)
        self.view.github_button.config(command=self.open_github_repo)

    # --------------------- Core Functionality ---------------------
    @catch_errors
    def handle_video_selection(self):
        """Initiate video processing workflow"""
        if self.processing_active:
            messagebox.showinfo(
                "Operation In Progress",
                "Please wait for current processing to complete"
            )
            return

        if file_path := filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        ):
            self.processing_active = True
            threading.Thread(
                target=self.process_video,
                args=(file_path,),
                daemon=True
            ).start()

    def process_video(self, video_path):
        """Execute video processing pipeline"""
        try:
            # Audio extraction phase
            check_ffmpeg()
            audio_path = extract_audio(video_path)
            
            # Transcription phase
            transcription = self.transcriber.transcribe(audio_path)
            
            # Save results
            if save_path := filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            ):
                save_transcription(transcription, save_path)
                messagebox.showinfo(
                    "Success", 
                    "Transcription saved successfully!"
                )

        except Exception as e:
            error_info = format_error(e)
            messagebox.showerror(
                f"Error {error_info['code']}",
                error_info['message']
            )
        finally:
            self.processing_active = False

    # --------------------- System Operations ---------------------
    def open_github_repo(self):
        """Launch project repository in default browser"""
        webbrowser.open(constants.URLS["github_repo"])