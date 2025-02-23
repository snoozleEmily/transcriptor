import sys
import tkinter as tk

try:
    from app.gui import TranscriptorApp
    from app.controller import ProcessingController
except ImportError as e:
    print(f"Error: {e}")
    print("Please ensure all dependencies are installed. Run: pip install -r requirements.txt")
    sys.exit(1)

def main():
    root = tk.Tk()
    controller = ProcessingController()
    TranscriptorApp(root, controller)
    root.mainloop()

if __name__ == "__main__":
    main()