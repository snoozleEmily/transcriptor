from pathlib import Path



def get_requirements():
    reqs_path = Path(__file__).parent.parent / "requirements.txt"
    with open(reqs_path, "r", encoding="utf-8") as f:
        return [
            line.split("#", 1)[0].strip()
            for line in f
            if line.strip() and not line.startswith(("#", "-"))
        ]