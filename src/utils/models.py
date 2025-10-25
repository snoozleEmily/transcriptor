from typing import Dict


from src.logs.exceptions import TranscriptionError
from src.logs.debug import debug


# --------------------- Whisper ---------------------
# Integrated Whisper model configurations
WHISPER_MODELS: Dict[str, Dict] = {
    "tiny": {  # 0 - Fastest, lowest accuracy (~3M parameters)
        "name": "tiny",
        "accuracy_rank": 0,
        "parameters": "~3M",
        "speed_wps": 40.0,
        "setup_time": 1.0,  # Initialization time (seconds)
    },
    "base": {  # 1 - Very fast, low accuracy (~40M parameters)
        "name": "base",
        "accuracy_rank": 1,
        "parameters": "~40M",
        "speed_wps": 30.0,
        "setup_time": 2.5,
    },
    "small": {  # 2 - Moderate speed, medium accuracy (~74M parameters)
        "name": "small",
        "accuracy_rank": 2,
        "parameters": "~74M",
        "speed_wps": 18.0,
        "setup_time": 5.0,
    },
    "medium": {  # 3 - Slower, high accuracy (~155M parameters)
        "name": "medium",
        "accuracy_rank": 3,
        "parameters": "~155M",
        "speed_wps": 10.0,
        "setup_time": 12.0,
    },
    "large": {  # 4 - Slowest, highest accuracy (~300M parameters)
        "name": "large",
        "accuracy_rank": 4,
        "parameters": "~300M",
        "speed_wps": 5.0,
        "setup_time": 20.0,
    },
}

# For Time Estimation
MODEL_SPEEDS: Dict[str, float] = {name: model["speed_wps"] for name, model in WHISPER_MODELS.items()}
SETUP_TIMES: Dict[str, float] = {name: model["setup_time"] for name, model in WHISPER_MODELS.items()}

# --------------------- Llama Model Info ---------------------
LLAMA_MODELS: dict = {
    "3b": {
        "model_path": r"llm_models/llama-3.2-3b-instruct-q4_k_m.gguf",
        "speed": 40.0,  # tokens per second (smaller model, faster inference)
        "setup_time": 3.0,  # loading time in seconds
        "tokens": 4096,  # context_size
        "memory": "4-6GB RAM",  # RAM requirements
        "params": "3B",  # parameter count
        "description": "Compact and efficient, good for lightweight tasks or testing",
    }
}


# --------------------- Error Check ---------------------
def validate_whisper_models(models: Dict[str, Dict]):
    for name, config in models.items():
        if "speed_wps" not in config:
            raise TranscriptionError.missing_model_config(name, "speed_wps")

        if "setup_time" not in config:
            debug.dprint(f"Model '{name}' missing setup_time — defaulting to 0.0s")
            config["setup_time"] = 0.0

        debug.dprint(f"valid: {name} | speed: {config['speed_wps']} wps | setup: {config['setup_time']}s")

