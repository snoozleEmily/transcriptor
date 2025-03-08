import subprocess
import numpy as np
import noisereduce as nr
from io import BytesIO
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.exceptions import CouldntDecodeError


from errors.exceptions import FFmpegError, TranscriptionError



def check_ffmpeg() -> None:
    """Verify system has ffmpeg installed"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise FFmpegError.missing() from e
    except subprocess.TimeoutExpired as e:
        raise FFmpegError.timeout() from e

def extract_audio(video_path: str) -> AudioSegment:
    """Extract audio from video file"""
    try:
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", 
            "-ar", "16000", "-ac", "1",
            "-f", "wav", "pipe:1"
        ]
        
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        return AudioSegment.from_wav(BytesIO(result.stdout))
    
    except subprocess.TimeoutExpired as e:
        raise FFmpegError.extraction_failed("Audio extraction timed out") from e
    except (subprocess.CalledProcessError, CouldntDecodeError) as e:
        raise FFmpegError.extraction_failed("Invalid media format") from e

def clean_audio(audio: AudioSegment) -> AudioSegment:
    """Remove noise and silence from audio"""
    try:
        samples = np.array(audio.get_array_of_samples())
        cleaned = nr.reduce_noise(y=samples, sr=audio.frame_rate)
        
        return AudioSegment(
            cleaned.tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=audio.sample_width,
            channels=1
        )
    except Exception as e:
        raise TranscriptionError.cleanup_failed() from e