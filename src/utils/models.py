from typing import List, Dict


from src.errors.exceptions import TranscriptionError
from src.errors.debug import debug



# --------------------- Whisper ---------------------
# Integrated Whisper model configurations
WHISPER_MODELS: Dict[str, Dict[str, any]] = {
    "tiny": {  # 0 - Fastest, lowest accuracy (~3M parameters)
        "accuracy_rank": 0,
        "parameters": "~3M",
        "speed_wps": 40.0, 
        "setup_time": 1.0,  # Initialization time (seconds)
    },
    "base": {  # 1 - Very fast, low accuracy (~40M parameters)
        "accuracy_rank": 1,
        "parameters": "~40M",
        "speed_wps": 30.0,  
        "setup_time": 2.5,
    },
    "small": {  # 2 - Moderate speed, medium accuracy (~74M parameters)
        "accuracy_rank": 2,
        "parameters": "~74M",
        "speed_wps": 18.0,
        "setup_time": 5.0,
    },
    "medium": {  # 3 - Slower, high accuracy (~155M parameters)
        "accuracy_rank": 3,
        "parameters": "~155M",
        "speed_wps": 10.0,
        "setup_time": 12.0,
    },
    "large": {  # 4 - Slowest, highest accuracy (~300M parameters)
        "accuracy_rank": 4,
        "parameters": "~300M",
        "speed_wps": 5.0,
        "setup_time": 20.0,
    }
}

# To be removed
# Maintain backward compatibility with original variable names
WHISPER_MODEL_NAMES: List[str] = list(WHISPER_MODELS.keys())
MODEL_SPEEDS: Dict[str, float] = {name: model["speed_wps"] for name, model in WHISPER_MODELS.items()}
SETUP_TIMES: Dict[str, float] = {name: model["setup_time"] for name, model in WHISPER_MODELS.items()}


# --------------------- Llama Model Info ---------------------
LLAMA_MODELS: dict = {
    "7b": {
        "model_path": "D:\\Projects\\Python-studies\\transcriptor\\llm_models\\llama-2-7b.Q4_K_M.gguf",  
        "speed": 25.0,           # tokens per second
        "setup_time": 5.0,       # loading time in seconds
        "tokens": 4096,          # context_size
        "memory": "8-12GB RAM",  # RAM requirements
        "params": "7B",          # parameter count
        "description": "Fast inference, good for most tasks",
    }
}
# --------------------- Error Check ---------------------
# Check for missing configurations (using the original variables)
for model in WHISPER_MODEL_NAMES:
    if model not in MODEL_SPEEDS:
        raise TranscriptionError.missing_model_config(model, "speed")

    if model not in SETUP_TIMES:
        raise TranscriptionError.missing_model_config(model, "setup_time")

    if model not in SETUP_TIMES:
        SETUP_TIMES[model] = 0.0  # Default setup for missing entries
        print("Missing entries detected. Using default.")
        
        debug.dprint(f"Model '{model}' was missing setup time. Defaulted to 0.0s.")
        debug.dprint(f"Current MODEL_SPEEDS: {MODEL_SPEEDS[model]} wps, SETUP_TIMES: {SETUP_TIMES[model]}s")


# --------------------- Constants For User ---------------------
# TODO: Implement this info to be achievable through the interface
MODELS_INFO = {
    "whisper": {
        "tiny": [0, "Fastest", "Lowest accuracy", "~3M parameters"],
        "base": [1, "Very fast", "Low accuracy", "~40M parameters"],
        "small": [2, "Moderate speed", "Medium accuracy", "~74M parameters"],
        "medium": [3, "Slower", "High accuracy", "~155M parameters"],
        "large": [4, "Slowest", "Highest accuracy", "~300M parameters"],
    },
    "llama": {
        "7b": [
            0,
            "Fast inference",
            "7B parameters",
            "8-12GB RAM",
            LLAMA_MODELS["7b"]["description"],
        ]
    },
}