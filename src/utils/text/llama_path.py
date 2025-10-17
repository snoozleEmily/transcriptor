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

    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    cfg = Path(config_path)

    candidates = []
    if cfg.is_absolute():
        candidates.append(cfg)

    candidates.append(base_dir / cfg)                  # relative to package/exe
    candidates.append(base_dir / "models" / cfg.name)  # models/ next to package/exe
    candidates.append(Path.cwd() / cfg)                # current working dir
    candidates.append(Path.home() / cfg.name)          # user's home

    # additional local directories
    candidates = [p.resolve() for p in candidates]

    for p in candidates:
        if p.exists():
            debug.dprint(f"Candidate model found at: {p}")
            return str(p)

    # not found -> helpful error
    checked = "\n".join(str(p) for p in candidates)
    raise FileNotFoundError( # TODO: Handle this err properly in exceptions module
        f"Model not found. looked for:\n{checked}\n\n"
        "Fix options:\n"
        " • Put the model file at one of the listed paths (recommended: project/models/).\n"
        " • Set LLAMA_MODEL_PATH env var to the exact file path.\n"
        " • Use an absolute path in LLAMA_MODELS for model_path."
    )
