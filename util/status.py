from enum import Enum


class Status(Enum):
    SUCCESS = "Process completed successfully."
    AUDIO_FAIL = "Audio extraction failed."
    FFMPEG_MISSING = "ffmpeg not found. Install from https://ffmpeg.org/"
    TRANSCRIPTION_FAIL = "Transcription failed."
    FILE_SAVE_FAIL = "Failed to save transcription."

    @staticmethod
    def get_ffmpeg_command(video_path, audio_path):
        """Returns the FFmpeg command for audio extraction."""
        return [
            "ffmpeg",
            "-y",  # Overwrite output file without asking
            "-i", video_path,
            "-vn",  # Disable video processing
            "-acodec", "pcm_s16le",  # WAV format
            "-ar", "16000",  # Sample rate
            "-ac", "1",  # Mono audio
            audio_path,
        ]