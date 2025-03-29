from tkinter import ttk



class Header(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        ttk.Label(
            self,
            text="EMILY'S TRANSCRIPTOR",
            style="HeaderTitle.TLabel"
        ).pack(pady=(0, 5))
        
        ttk.Label(
            self,
            text="🎥",
            style="EmojiDisplay.TLabel"  
        ).pack(pady=(0, 35))