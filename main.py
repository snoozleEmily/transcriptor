import tkinter as tk


from app.gui import Interface
from app.controller import ProcessingController


#.\venv\Scripts\activate

def main():
    root = tk.Tk()
    controller = ProcessingController()
    Interface(controller)
    root.mainloop()

if __name__ == "__main__":
    main()