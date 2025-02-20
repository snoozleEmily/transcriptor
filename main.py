import os
import subprocess
import textwrap
import speech_recognition as sr

from util.status import Status
from util.errors import (
    FfmpegMissingError, AudioExtractionError, TranscriptionError,
    FileSaveError, transcription_error_handler, handle_error
)



def check_ffmpeg() -> None:
    """
    Verify that ffmpeg is available in the system PATH.
    Raises:
        FfmpegMissingError: If ffmpeg is not found.
    """
    result = subprocess.run(
        ["ffmpeg", "-version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    if result.returncode != 0:
        raise FfmpegMissingError()

def extract_audio(video_path: str, audio_path: str) -> None:
    """
    Extract audio from the given video using ffmpeg.
    Raises:
        AudioExtractionError: If ffmpeg fails to extract audio.
    """
    cmd = Status.get_ffmpeg_command(video_path, audio_path)
    result = subprocess.run(cmd, check=False, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise AudioExtractionError(f"ffmpeg error: {result.stderr.decode()[:100]}")

@transcription_error_handler
def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio using Google's Speech Recognition.
    
    This function is decorated with transcription_error_handler, which 
    converts specific errors into a TranscriptionError.
    
    Returns:
        str: The transcribed text.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        return recognizer.recognize_google(audio)

def save_transcription(text: str, output_path: str, line_width: int = 80) -> None:
    """
    Save the transcribed text to a file with text wrapping.
    
    Raises:
        FileSaveError: If the transcription cannot be saved.
    """
    wrapped_text = textwrap.fill(text, width=line_width)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(wrapped_text)
    except Exception as e:
        raise FileSaveError(f"File save error: {str(e)}")

def process_media(video_path: str, output_txt_path: str) -> str:
    """
    Process the media file by extracting audio, transcribing it, and saving the transcription.
    
    Returns:
        str: A success message if the process completes, or an error message from errors module.
    """
    try:
        check_ffmpeg()
        audio_path = "temp_audio.wav"
        extract_audio(video_path, audio_path)
        transcription = transcribe_audio(audio_path)
        save_transcription(transcription, output_txt_path)

        # Clean up temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return Status.SUCCESS.value

    except (FfmpegMissingError, AudioExtractionError, TranscriptionError, FileSaveError) as e:
        # Delegate exception handling to the centralized handler
        return handle_error(e)

if __name__ == "__main__":
    video_path = input("Enter video file path: ").strip()
    output_path = "transcription.txt"
    result_message = process_media(video_path, output_path)
    print(result_message)
