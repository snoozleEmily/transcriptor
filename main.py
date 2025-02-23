import tkinter as tk


from app.gui import TranscriptorApp
from app.controller import ProcessingController


#.\venv\Scripts\activate

def main():
    root = tk.Tk()
    controller = ProcessingController()
    TranscriptorApp(root, controller)
    root.mainloop()

if __name__ == "__main__":
    main()