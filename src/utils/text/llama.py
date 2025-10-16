from __future__ import annotations
from threading import Lock
from typing import Optional

from llama_cpp import Llama as Llm
from llama_cpp import CreateChatCompletionResponse


from src.logs.debug import debug
from src.utils.models import LLAMA_MODELS
from .llama_path import resolve_model_path


AVERAGE_CHARS_PER_TOKEN = 4.0
SUMMARY_RATIO = 0.18
MIN_SUMMARY_TOKENS = 32
MAX_SUMMARY_TOKENS = 1024
SAFETY_MARGIN = 64
CONTENT = {
    "system": (
        "You are a precise summarizer. FOLLOW THESE RULES EXACTLY:\n"
        "1. Output EXACTLY one line containing only the summary text and nothing else.\n"
        "2. Do NOT prepend or append any phrase such as 'Here is the summary', 'Summary:', 'TL;DR', or similar.\n"
        "3. Do NOT use quotes, headings, code blocks, or extra whitespace.\n"
        "4. Keep the summary in the original language of the input.\n"
        "5. If you must shorten to meet token limits, truncate the summary only — do NOT comment about truncation."
    ),
    "user": "Summarize this text in one concise sentence. Output only the summary itself:\n\n",
}


class Llama:
    """Singleton wrapper for the LLaMA model."""

    _instance = None  # Holds the single instance of this class
    _lock = Lock()  # Ensures thread-safe instantiation

    def __new__(cls):
        """Ensure only one instance of Llama exists (singleton pattern)."""
        with cls._lock:  # Acquire lock for thread safety
            if cls._instance is None:  # Create instance only if it doesn't exist
                cls._instance = super().__new__(cls)
                debug.dprint(f"Llama singleton instance created.")

        return cls._instance

    def __init__(self, model_size: str = "3b"):
        """Initialize model metadata and prepare for lazy loading."""
        # avoid re-initializing singleton
        if getattr(self, "_initialized", False):
            return

        self.model_size = model_size
        self._model = None

        # Metadata
        self._model_path: Optional[str] = None
        self._model_ctx: Optional[int] = None

        self._initialized = True
        debug.dprint(f"Llama initialized for lazy loading, model_size={model_size}")
        print("🛠️ Preparing the AI engine. This may take a moment…")

    @property
    def model(self):
        """Lazy-load and return the LLaMA model instance."""
        if self._model is None:
            debug.dprint(f"Loading LLaMA model '{self.model_size}' now...")
            model_config = LLAMA_MODELS.get(self.model_size, LLAMA_MODELS["3b"])
            raw_path = model_config.get("model_path", "models/ggml-7b-model.bin")
            ctx_size = int(model_config.get("tokens", 4096))
            model_path = resolve_model_path(
                raw_path
            )  # raises FileNotFoundError if missing

            self._model = Llm(
                model_path=model_path,
                n_ctx=ctx_size,
                verbose=False,
            )

            self._model_path = model_path
            self._model_ctx = ctx_size

            debug.dprint(f"LLaMA model '{self.model_size}' loaded.")
            print(f"✅ AI model '{self.model_size}' loaded successfully.")

        return self._model

    # ---------------------------
    # Token estimation utilities
    # ---------------------------
    def _estimate_input_tokens(self, text: str) -> int:
        """Estimate token count for given text using tiktoken or a heuristic fallback."""
        if not text:
            fallback = 0
            debug.dprint(
                f"The transcription is not a valid value: {text}.\n"
                f"Using fallback token count: {fallback}"
            )
            return fallback

        try:
            import tiktoken

            print("📝 Processing your notes… Almost there!") 

            try:
                enc = tiktoken.get_encoding("cl100k_base")
                token_count = len(enc.encode(text))
                debug.dprint(f"tiktoken successfully used: {token_count} tokens")
                
            except Exception as e:
                debug.dprint(
                    f"tiktoken encoding lookup failed; falling back to gpt-3.5-turbo encoding. Error: {e}"
                )
                enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

            token_count = len(enc.encode(text))
            debug.dprint(
                f"Token estimate using tiktoken: {token_count} tokens for {len(text)} chars."
            )
            
            return token_count

        except Exception as e:
            token_count = max(1, int(len(text) / AVERAGE_CHARS_PER_TOKEN))
            print(
            "⚠️ Token estimation fallback is in use. "
            "Results may be less accurate. Please OPEN AN ISSUE this if it persists."
            "Exception: {e}"
                )  # Signal problem in prod
            debug.dprint(
                f"Token estimate using heuristic: {token_count} tokens "
                f"(chars={len(text)}, avg_chars_per_token={AVERAGE_CHARS_PER_TOKEN}). "
                f"Error: {e}"
            )
            return token_count

    def _available_context_tokens(self) -> int:
        """Return the model’s available context size in tokens."""
        if self._model_ctx is not None:
            return int(self._model_ctx)

        model_conf_raw = LLAMA_MODELS.get(self.model_size, LLAMA_MODELS["3b"])
        return int(model_conf_raw.get("tokens", 4096))

    def compute_max_summary_tokens(
        self, text: str, explicit_max_tokens: Optional[int]
    ) -> int:
        """Compute safe maximum token count for summarization based on input size and context."""
        if explicit_max_tokens is not None:
            ctx = self._available_context_tokens()
            safe_max = max(1, ctx - SAFETY_MARGIN)
            chosen = max(
                MIN_SUMMARY_TOKENS,
                min(explicit_max_tokens, safe_max, MAX_SUMMARY_TOKENS),
            )
            debug.dprint(
                f"Explicit max_tokens provided: {explicit_max_tokens} -> chosen {chosen}"
            )
            return chosen

        input_tokens = self._estimate_input_tokens(text)

        if input_tokens <= 64:
            chosen = min(MAX_SUMMARY_TOKENS, max(MIN_SUMMARY_TOKENS, 32))
            debug.dprint(
                f"Very short input: {input_tokens} tokens -> max_tokens={chosen}"
            )
            return chosen

        target = max(MIN_SUMMARY_TOKENS, int(input_tokens * SUMMARY_RATIO))
        ctx = self._available_context_tokens()
        safe_max = max(1, ctx - SAFETY_MARGIN)
        chosen = min(target, safe_max, MAX_SUMMARY_TOKENS)

        debug.dprint(
            f"Computed max_tokens: input_tokens={input_tokens}, target={target}, "
            f"ctx={ctx}, safety_margin={SAFETY_MARGIN}, chosen={chosen}"
        )
        return chosen

    # ---------------------------
    # Summarization API
    # ---------------------------
    def summarize_text(self, text: str, max_tokens: Optional[int] = None) -> str:
        """Generate a concise summary of the given text."""
        if not text:
            return ""

        computed_max = self.compute_max_summary_tokens(
            text, explicit_max_tokens=max_tokens
        )
        debug.dprint(
            f"Summarizing text of length={len(text)}, max_tokens={computed_max}"
        )

        system_message = {"role": "system", "content": CONTENT["system"]}

        user_message = {
            "role": "user",
            "content": CONTENT["user"] + text,
        }

        response: CreateChatCompletionResponse = self.model.create_chat_completion(
            messages=[system_message, user_message],
            max_tokens=computed_max,
            temperature=0,
            stream=False,
        )

        raw: str | None = response["choices"][0]["message"].get("content")
        return self._clean_summary(raw)  # type: ignore

    # ---------------------------
    # Utilities
    # ---------------------------
    def _clean_summary(self, text: str) -> str:
        """Clean summary text by removing redundant prefixes or formatting."""
        import re

        if not text:
            return ""

        text = text.strip()
        text = re.sub(r"^(here is (the )?summary[:\-\s]*)", "", text, flags=re.I)
        text = re.sub(r"^(summary[:\-\s]*)", "", text, flags=re.I)
        return text.splitlines()[0].strip()


llama: Llama = Llama()
