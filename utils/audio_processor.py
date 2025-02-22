import subprocess
from io import BytesIO
from typing import Optional
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from .status import Status
from errors.exceptions import FFmpegError



def check_ffmpeg() -> None:
    """Verify system has ffmpeg installed and accessible"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise FFmpegError.missing() from e

def extract_audio(video_path: str) -> Optional[AudioSegment]:
    """
    Extract audio from video file to in-memory AudioSegment
    Returns:
        AudioSegment: Raw audio data
    Raises:
        FFmpegError: If extraction fails
    """
    # Check sanitized path
    print(f"Extracting audio from: {video_path}")
    
    try:
        cmd = Status.get_ffmpeg_command(video_path)
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            timeout=30  # Fail if processing takes >30s
        )
        return AudioSegment.from_wav(BytesIO(result.stdout))
    
    except subprocess.TimeoutExpired as e:
        raise FFmpegError.extraction_failed("Audio extraction timed out") from e
    
    except (subprocess.CalledProcessError, CouldntDecodeError) as e:
        raise FFmpegError.extraction_failed("Invalid media format") from e
    
    except Exception as e:
        raise FFmpegError.extraction_failed("Unknown extraction error") from e