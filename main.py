import textwrap

from utils.audio_processor import check_ffmpeg, extract_audio
from utils.transcriber import Transcriber
from utils import errors, status


# For devs to copy and  ctrl -v: 
# .\venv\Scripts\Activate
# deactivate


def save_transcription(text: str, output_path: str):
    """Save formatted transcription"""
    try:
        wrapped = textwrap.fill(text, width=80)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(wrapped)
        return status.Status.SUCCESS.value
    except Exception as e:
        raise errors.FileSaveError(str(e))

def process_media(video_path: str, output_path: str) -> str:
    """Main processing pipeline"""
    try:
        check_ffmpeg()
        audio = extract_audio(video_path)
        transcriber = Transcriber(model_size="tiny")
        text = transcriber.transcribe(audio)
        return save_transcription(text, output_path)
    except Exception as e:
        return errors.handle_error(e)

if __name__ == "__main__":
    video_path = input("Enter video path: ").strip()
    result = process_media(video_path, "transcription.txt")
    print(result)