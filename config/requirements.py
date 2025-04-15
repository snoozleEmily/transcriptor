import chardet
from pathlib import Path



def get_requirements():
    reqs_path = Path(__file__).parent.parent / "requirements.txt"
    
    # Detect encoding first
    with open(reqs_path, "rb") as f:
        raw_data = f.read()
        encoding = chardet.detect(raw_data)["encoding"]
    
    # Read with detected encoding
    with open(reqs_path, "r", encoding=encoding) as f:
        return [
            line.split("#", 1)[0].strip()
            for line in f
            if line.strip() and not line.startswith(("#", "-"))
        ]
    
if __name__ == "__main__":
    print(get_requirements())