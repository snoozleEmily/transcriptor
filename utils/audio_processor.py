import subprocess
from pydub import AudioSegment

from status import Status
from .errors import AudioExtractionError, FfmpegMissingError

def check_ffmpeg():
    """Verify ffmpeg is installed"""
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise FfmpegMissingError()

def extract_audio(video_path: str) -> AudioSegment:
    """Extract audio directly to memory"""
    try:
        cmd = Status.get_ffmpeg_command(video_path)
        result = subprocess.run(cmd, check=True, capture_output=True)
        return AudioSegment.from_wav(BytesIO(result.stdout))
    except Exception as e:
        raise AudioExtractionError(str(e))