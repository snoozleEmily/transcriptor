from typing import Dict, Any


from src.logs.debug import debug
from src.utils.transcripting.loader import Loader


def transcribe_audio(
    audio: Any, context_prompt: str, transcriber, model_size, content_config, **kwargs
) -> Dict[str, Any]:
    """Execute transcription with proper error context."""
    print("Getting everything ready...")

    loader = Loader()

    loader.setup(transcribe_estimate=3.0, what="Loading Transcriptor")
    loader.start_transcription_progress()

    if transcriber and getattr(transcriber, "model_size", None) == model_size:
        debug.dprint("Reusing cached transcriber.")

    else:
        from src.utils.transcripting.textify import Textify

        transcriber = Textify(model_size)

        result = {"status": "success"}
        loader.complete(result, duration=3.0)
        debug.dprint(
            "Textify loaded in transcribe_audio as: {transcriber} | audio: {audio}"
        )

    return transcriber.transcribe(
        audio,
        initial_prompt=context_prompt,
        temperature=0.2 if content_config.types else 0.5,
        **kwargs,
    )
