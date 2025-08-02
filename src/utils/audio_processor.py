import subprocess
import numpy as np
import noisereduce as nr
from io import BytesIO
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError


from src.errors.exceptions import FFmpegError, TranscriptionError, ErrorCode



def check_ffmpeg() -> None:
    """Verify system has ffmpeg installed"""
    try:
        # Check if FFmpeg is installed and working
        subprocess.run(
            ["ffmpeg", "-version"],  # Basic command to check FFmpeg
            check=True,  # Raise error if command fails
            stdout=subprocess.DEVNULL,  # Hide version output
            stderr=subprocess.DEVNULL,  # Hide error messages
            timeout=5,  # Wait max 5 seconds
        )

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise FFmpegError(
            code=ErrorCode.FFMPEG_ERROR,
            message="FFmpeg not found in system PATH",
            context={"installation_guide": "https://ffmpeg.org/download.html"},
        ) from e

    except subprocess.TimeoutExpired as e:
        raise FFmpegError(
            code=ErrorCode.FFMPEG_ERROR,
            message="FFmpeg version check timed out",
            context={"timeout_seconds": 5},
        ) from e


def extract_audio(video_path: str) -> AudioSegment:
    """Extract audio from video file using FFmpeg

    Args:
        video_path: Path to the input video file

    Returns:
        AudioSegment: Extracted audio in WAV format

    Raises:
        FFmpegError: If extraction fails
        TranscriptionError: If audio decoding fails
    """
    try:
        cmd = [
            "ffmpeg",  # FFmpeg executable
            "-y",  # Auto-overwrite output files without asking
            "-i",
            video_path,  # Input file path

            # Audio extraction options:
            "-vn",  # Disable video processing (video no)
            "-acodec",
            "pcm_s16le",  # Audio codec: 16-bit little-endian PCM
            "-ar",
            "16000",  # Audio sample rate: 16kHz (optimal for speech)
            "-ac",
            "1",  # Audio channels: 1 (mono)
            
            # Output format:
            "-f",
            "wav",  # Output format: WAV container
            "pipe:1",  # Output to stdout (for Python processing)
        ]

        result = subprocess.run(
            cmd,
            check=True,  # Raise exception if command fails
            stdout=subprocess.PIPE,  # Capture stdout (audio data)
            stderr=subprocess.PIPE,  # Capture stderr (for error reporting)
            timeout=30,  # Maximum execution time (seconds)
        )

        # Convert binary stdout to AudioSegment
        return AudioSegment.from_wav(BytesIO(result.stdout))

    except subprocess.TimeoutExpired as e:
        raise FFmpegError(
            code=ErrorCode.FFMPEG_ERROR,
            message="Audio extraction timed out",
            context={"timeout_seconds": 30},
        ) from e

    except subprocess.CalledProcessError as e:
        raise FFmpegError.from_ffmpeg_output(output=e.stderr.decode().strip()) from e

    except CouldntDecodeError as e:
        raise TranscriptionError.load_failed(error=e) from e


def clean_audio(audio: AudioSegment) -> AudioSegment:
    """Audio preprocessing pipeline"""
    try:
        # Convert to numpy array for processing
        samples = np.array(audio.get_array_of_samples())

        # Main noise reduction (works best for constant background noise)
        cleaned = nr.reduce_noise(
            y=samples,  # Audio samples as numbers
            sr=audio.frame_rate,  # Keep original sample rate (e.g. 16000)
            stationary=True,  # Best for steady noise like fans/AC
        )

        # Convert back to audio format
        return AudioSegment(
            cleaned.tobytes(),  # Processed audio data
            frame_rate=audio.frame_rate,  # Same sample rate as input
            sample_width=2,  # Standard 16-bit audio (2 bytes per sample)
            channels=1,  # Mono audio
        )

    except Exception as e:
        raise TranscriptionError.progress_tracking(error=e) from e
