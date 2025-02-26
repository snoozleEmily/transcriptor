from core.gui import Interface
from core.controller import ProcessingController


#.\venv\Scripts\activate

def main():
    controller = ProcessingController()
    app = Interface(controller)
    app.mainloop()

if __name__ == "__main__":
    main()