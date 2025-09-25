from threading import Lock
from llama_cpp import Llama as Llm
from llama_cpp import CreateChatCompletionResponse


from src.errors.debug import debug
from src.utils.models import LLAMA_MODELS
from .llama_path import resolve_model_path

# Call it in notes generator for summarization


class Llama:
    """Singleton wrapper for the LLaMA model."""

    _instance = None  # Holds the single instance of this class
    _lock = Lock()  # Ensures thread-safe instantiation

    def __new__(cls):
        with cls._lock:  # Acquire lock for thread safety
            if cls._instance is None:  # Create instance only if it doesn't exist
                cls._instance = super().__new__(cls)
                debug.dprint(f"Llama singleton instance created.")

        return cls._instance

    def __init__(self, model_size: str = "7b"):
        # avoid re-initializing singleton
        if getattr(self, "_initialized", False):
            return

        debug.dprint(f"Initializing Llama with model_size={model_size}")

        model_config = LLAMA_MODELS.get(model_size, LLAMA_MODELS["7b"])
        raw_path = model_config.get("model_path", "models/ggml-7b-model.bin")
        ctx_size = int(model_config.get("tokens", 4096))

        model_path = resolve_model_path(raw_path)  # raises FileNotFoundError if missing

        # instantiates the Llm wrapper
        self.model = Llm(model_path=model_path, n_ctx=ctx_size, verbose=False)
        self.model_size = model_size
        self._initialized = True

        debug.dprint(
            f"Llm instance created for model_size={model_size}, model_path={model_path}"
        )

    def generate(self, prompt: str, max_tokens) -> str:
        response: CreateChatCompletionResponse = self.model.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes transcription text concisely.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            stream=False,
        )
        content = response["choices"][0]["message"]["content"]
        return content.strip() if content else ""


llama: Llama = Llama()
