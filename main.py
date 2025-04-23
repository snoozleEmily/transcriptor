from src.frontend.interface import Interface
from src.utils.end_flow import EndFlow


# Activate virtual environment
#.\venv\Scripts\activate

def main():
    ef = EndFlow()
    app = Interface(ef)
    app.mainloop()

if __name__ == "__main__":
    main()

    