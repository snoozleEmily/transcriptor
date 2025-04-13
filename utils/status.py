from enum import Enum

# Do I really need this module?

class Status(Enum):
    PROCESSING = "⏳ Processing..."
    EXTRACTING = "🔊 Extracting audio"
    CLEANING = "🎧 Cleaning audio"
    TRANSCRIBING = "📝 Transcribing"
    SUCCESS = "✅ Success"
    FAILED = "❌ Failed"