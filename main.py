from src.frontend.interface import Interface
from src.utils.controller import ProcessingController



# Activate virtual environment
#.\venv\Scripts\activate

def main(): # It has breaking changes
    controller = ProcessingController()
    app = Interface(controller)
    app.mainloop()

if __name__ == "__main__":
    main()

    