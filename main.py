import os
import ffmpeg 
import whisper
from fpdf import FPDF
from enum import Enum

class Status(Enum):
    SUCCESS = "Process completed successfully."
    AUDIO_FAIL = "Audio extraction failed. Exiting."
    TRANSCRIPTION_FAIL = "Transcription failed."
    PDF_FAIL = "Failed to save transcription to PDF."

def extract_audio(video_path, audio_path):
    """Extracts and saves audio from a video file using ffmpeg-python with error handling."""
    try:
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(stream, audio_path, format='mp3', acodec='mp3')
        ffmpeg.run(stream, overwrite_output=True)
        return {"success": True, "message": f"Audio extracted and saved to {audio_path}"}
    except ffmpeg.Error as e:
        print("FFmpeg Error:", e.stderr.decode())
        return {"success": False, "message": f"Error extracting audio: {e.stderr.decode()}"}


def transcribe_audio(audio_path, model_name="base"):
    """
    Transcribes an audio file to text using OpenAI's Whisper.
    """
    try:
        model = whisper.load_model(model_name)
        print(f"Loaded Whisper model: {model_name}")
        result = model.transcribe(audio_path)
        print("Transcription completed.")
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio with Whisper: {e}")
        return ""

def save_to_pdf(text, output_pdf_path):
    """
    Saves the transcribed text to a PDF file.
    """
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        
        lines = text.splitlines()
        for line in lines:
            pdf.multi_cell(0, 10, line)

        pdf.output(output_pdf_path)
        print(f"Transcription saved to PDF: {output_pdf_path}")
        return True
    except Exception as e:
        print(f"Error saving transcription to PDF: {e}")
        return False

def process_transcription(video_path, audio_path, output_pdf_path):
    audio_result = extract_audio(video_path, audio_path)
    if not audio_result["success"]:
        return audio_result["message"]

    transcription = transcribe_audio(audio_path, model_name="base")
    if not transcription:
        return Status.TRANSCRIPTION_FAIL.value

    if not save_to_pdf(transcription, output_pdf_path):
        return Status.PDF_FAIL.value

    return Status.SUCCESS.value

if __name__ == "__main__":
    video_path = input("Enter the path to the video file: ").strip()
    audio_path = "extracted_audio.mp3"
    output_pdf_path = "transcription.pdf"
    
    print(process_transcription(video_path, audio_path, output_pdf_path))
    
    if os.path.exists(audio_path):
        try:
            os.remove(audio_path)
            print(f"Temporary audio file {audio_path} deleted.")
        except Exception as e:
            print(f"Error deleting temporary audio file: {e}")
