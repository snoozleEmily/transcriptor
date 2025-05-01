from tkinter import ttk

class Header(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        # Main container for centering
        container = ttk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Video emoji
        ttk.Label(
            container,
            text="🎥",
            style="EmojiDisplay.TLabel"
        ).pack(pady=(0, 5))
        
        # Title
        ttk.Label(
            container,
            text="EMILY'S TRANSCRIPTOR",
            style="HeaderTitle.TLabel"
        ).pack(pady=(0, 35))