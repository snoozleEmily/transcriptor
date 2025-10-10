from threading import Lock
from llama_cpp import Llama as Llm
from llama_cpp import CreateChatCompletionResponse


from src.errors.debug import debug
from src.utils.models import LLAMA_MODELS
from .llama_path import resolve_model_path



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

    def summarize_text(self, text: str, max_tokens: int = 80) -> str:
        """Generate a concise summary following strict formatting rules."""
        system_message = {
            "role": "system",
            "content": (
                "You are a precise summarizer. FOLLOW THESE RULES EXACTLY:\n"
                "1) Output EXACTLY one line containing only the summary text and nothing else.\n"
                "2) Do NOT prepend or append any phrase such as 'Here is the summary', 'Summary:', 'TL;DR', or similar.\n"
                "3) Do NOT use quotes, headings, code blocks, or extra whitespace.\n"
                "4) Keep the summary in the original language of the input.\n"
                "5) If you must shorten to meet token limits, truncate the summary only — do NOT comment about truncation."
            ),
        }

        user_message = {"role": "user", "content": text}

        response: CreateChatCompletionResponse = self.model.create_chat_completion(
            messages=[system_message, user_message],
            max_tokens=max_tokens,
            temperature=0,
            stream=False,
        )

        raw: str | None = response["choices"][0]["message"].get("content")
        return self._clean_summary(raw) # type: ignore


    def _clean_summary(self, text: str) -> str:
        """Remove unwanted prefixes and enforce single-line output."""
        import re

        if not text:
            return "" # handles None or empty string safely
        
        text = text.strip()
        text = re.sub(r"^(here is (the )?summary[:\-\s]*)", "", text, flags=re.I)
        text = re.sub(r"^(summary[:\-\s]*)", "", text, flags=re.I)
        return text.splitlines()[0].strip()


llama: Llama = Llama()
