from utils.transcriber import Transcriber
from utils.file_handler import save_transcription
from utils.audio_processor import check_ffmpeg, extract_audio
from errors.handlers import catch_errors, format_error

# For devs to copy and  ctrl -v: 
# .\venv\Scripts\Activate
# deactivate
# pip install -r requirements.txt

@catch_errors
def process_audio(video_path: str):
    """Process audio from video file"""
    check_ffmpeg()
    return extract_audio(video_path)


@catch_errors
def transcribe(audio) -> str:
    """Transcribe audio using Whisper"""
    transcriber = Transcriber(model_size="tiny")
    return transcriber.transcribe(audio)


def main():
    video_path = input("Enter video path: ").strip().strip('"').strip("'")
    try:
        # Step 1: Extract and clean audio
        audio = process_audio(video_path)
        
        # Step 2: Transcribe audio
        text = transcribe(audio)
        
        # Step 3: Save transcription
        save_transcription(text, "transcription.txt")
        print("✅ Transcription saved successfully!")
    
    except Exception as e:
        error_info = format_error(e)
        print(f"❌ Error {error_info['code']}: {error_info['message']}")


if __name__ == "__main__":
    main()