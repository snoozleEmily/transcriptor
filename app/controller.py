from utils import extract_audio, clean_audio, Transcriber, save_transcription
from errors.handlers import error_handler

class ProcessingController:
    def __init__(self):
        self.transcriber = Transcriber()

    @error_handler
    def process_video(self, video_path: str, progress_cb: callable):
        """Full processing pipeline with progress updates"""
        progress_cb(10, "Extracting audio...")
        audio = extract_audio(video_path)
        
        progress_cb(30, "Cleaning audio...")
        cleaned = clean_audio(audio)
        
        progress_cb(50, "Transcribing...")
        text = self.transcriber.transcribe(cleaned, 
            lambda p: progress_cb(50 + p*0.4, f"Transcribing ({int(p)}%)"))
        
        progress_cb(95, "Saving...")
        save_path = save_transcription(text)
        
        progress_cb(100, "Completed!")
        return save_path