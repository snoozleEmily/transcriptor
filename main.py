from frontend.interface import Interface
from frontend.controller import ProcessingController

# Activate virtual environment
#.\venv\Scripts\activate

def main(finish):
    controller = ProcessingController()
    app = Interface(controller, finish)
    app.mainloop()

if __name__ == "__main__":
    # You should treat this function somewhere else
    main(finish=lambda: print("Finished processing."))