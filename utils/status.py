from enum import Enum

class Status(Enum):
    SUCCESS = "✅ Process completed successfully!"
    FFMPEG_MISSING = "❌ ffmpeg not found. Install from https://ffmpeg.org/"
    AUDIO_FAIL = "❌ Audio extraction failed"
    TRANSCRIPTION_FAIL = "❌ Transcription failed"
    FILE_SAVE_FAIL = "❌ Failed to save transcription"
    
    @staticmethod
    def get_ffmpeg_command(video_path: str) -> list:
        return [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-f", "wav", "pipe:1"  # Output to stdout
        ]