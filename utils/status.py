from enum import Enum



class Status(Enum):
    PROCESSING = "⏳ Processing..."
    EXTRACTING = "🔊 Extracting audio"
    CLEANING = "🎧 Cleaning audio"
    TRANSCRIBING = "📝 Transcribing"
    SUCCESS = "✅ Success"
    FAILED = "❌ Failed"