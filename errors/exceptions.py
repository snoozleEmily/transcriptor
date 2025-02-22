class Errors(Exception):
    """Base exception for all transcriptor errors"""
    def __init__(self, code: str, message: str, cause: Exception = None):
        super().__init__(message)
        self.code = code
        self.cause = cause
        self.message = f"{message} [Code: {code}]"
        if cause:
            self.message += f"\nCause: {str(cause)}"

    def __str__(self):
        return self.message

# FFmpeg-related exceptions
class FFmpegError(Errors):
    @classmethod
    def missing(cls):
        return cls("FFMPEG_MISSING", "FFmpeg not installed")

    @classmethod
    def extraction_failed(cls, cause: Exception):
        return cls("AUDIO_EXTRACTION", "Audio extraction failed", cause)
    @classmethod
    def generic_error(cls, cause: Exception):
        return cls("FFMPEG_ERROR", "FFmpeg encountered an error", cause)
    
# Transcription-related exceptions
class TranscriptionError(Errors):
    @classmethod
    def no_speech(cls):
        return cls("NO_SPEECH", "No speech detected")

    @classmethod
    def service_error(cls, cause: Exception):
        return cls("SERVICE_ERROR", "Transcription service failed", cause)

    @classmethod
    def generic_error(cls, cause: Exception):
        return cls("TRANSCRIPTION_FAIL", "Transcription failed", cause)

# File-related exceptions
class FileError(Errors):
    @classmethod
    def save_failed(cls, cause: Exception):
        return cls("FILE_SAVE", "Failed to save file", cause)