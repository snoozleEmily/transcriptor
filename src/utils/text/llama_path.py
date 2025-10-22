from __future__ import annotations
from pathlib import Path
import sys
import os


from src.logs.debug import debug




def resolve_model_path(config_path: str | Path) -> str:
    """Return absolute model path found on disk or raise FileNotFoundError."""
    env_override = os.getenv("LLAMA_MODEL_PATH")
    if env_override:
        debug.dprint(f"LLAMA_MODEL_PATH override detected: {env_override}")
        p = Path(env_override)
        if not p.is_absolute():
            p = Path.cwd() / p
        if p.exists():
            debug.dprint(f"Model found via LLAMA_MODEL_PATH: {p}")
            return str(p)

    base_dir = Path(__file__).resolve()
    for parent in base_dir.parents:
        if (parent / "llm_models").exists():
            base_dir = parent
            break

    cfg = Path(config_path)

    candidates = [
        cfg if cfg.is_absolute() else base_dir / cfg,
        base_dir / "models" / cfg.name,
        base_dir / "llm_models" / cfg.name,
        Path.cwd() / cfg,
        Path.home() / cfg.name,
    ]

    for p in [c.resolve() for c in candidates]:
        if p.exists():
            debug.dprint(f"Candidate model found at: {p}")
            return str(p)

    checked = "\n".join(str(p) for p in candidates)
    raise FileNotFoundError(
        f"Model not found. looked for:\n{checked}\n\n"
        "Fix options:\n"
        " • Put the model file at one of the listed paths (recommended: root/llm_models/).\n"
        " • Set LLAMA_MODEL_PATH env var to the exact file path.\n"
        " • Use an absolute path in LLAMA_MODELS for model_path."
    )