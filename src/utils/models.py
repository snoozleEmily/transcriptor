from typing import List, Dict


from src.errors.exceptions import TranscriptionError



MODELS: List[str] = [
    "tiny",   # 0 - Fastest, lowest accuracy        ||||||||->  (~3M parameters)
    "base",   # 1 - Very fast, low accuracy         ||||||||->  (~40M parameters)
    "small",  # 2 - Moderate speed, medium accuracy ||||||||->  (~74M parameters)
    "medium", # 3 - Slower, high accuracy           ||||||||->  (~155M parameters)
    "large"   # 4 - Slowest, highest accuracy       ||||||||->  (~300M parameters)
]

# Implement this info for the user on the interface
MODELS_INFO = {
    "tiny":   [0, "Fastest", "Lowest accuracy", "~3M parameters"],
    "base":   [1, "Very fast", "Low accuracy", "~40M parameters"],
    "small":  [2, "Moderate speed", "Medium accuracy", "~74M parameters"],
    "medium": [3, "Slower", "High accuracy", "~155M parameters"],
    "large":  [4, "Slowest", "Highest accuracy", "~300M parameters"]
}

MODEL_SPEEDS: Dict[str, float] = {
    # Words per second based on mid-range GPU benchmarks
    # Used to estimate transcription time: wall_time ≈ word_count / wps

    "tiny":   40.0,  # Ultra-fast, minimal resource use
    "base":   30.0,  # Fast, lightweight
    "small":  18.0,  # Balanced performance
    "medium": 10.0,  # Slower, higher accuracy
    "large":   5.0   # Slowest, most accurate

}

SETUP_TIMES: Dict[str, float] = {
    # Initialization times (seconds) 
    "tiny":    1.0,
    "base":    2.5,
    "small":   5.0,
    "medium": 12.0,
    "large":  20.0
}

# --------------------- Error Check ---------------------
for model in MODELS: # Ensure all models have speed and setup entries
    if model not in MODEL_SPEEDS:
        raise TranscriptionError.missing_model_config(model, "speed")
    
    if model not in SETUP_TIMES:
        raise TranscriptionError.missing_model_config(model, "setup_time")
    
    if model not in SETUP_TIMES:
        SETUP_TIMES[model] = 0.0  # Default setup for missing entries
        print("Missing entries detected. Using default.") # No error should be raised here