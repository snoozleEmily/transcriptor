from enum import Enum

# Add these to the logs

class Status(Enum):
    PROCESSING = "⏳ Processing..."
    EXTRACTING = "🔊 Extracting audio"
    CLEANING = "🎧 Cleaning audio"
    TRANSCRIBING = "📝 Transcribing"
    SUCCESS = "✅ Success"
    FAILED = "❌ Failed"