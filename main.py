from src.frontend.interface import Interface
from src.utils.end_flow import EndFlow


# Activate virtual environment
# .\venv\Scripts\Activate.ps1


def main():
    ef = EndFlow()
    app = Interface(ef)
    app.mainloop()

if __name__ == "__main__":
    main()