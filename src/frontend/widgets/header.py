from tkinter import ttk


from src.frontend.constants import FONTS



class Header(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure_style()
        self._create_widgets()
    
    def configure_style(self):
        style = ttk.Style()
        style.configure(
            "HeaderTitle.TLabel",
            font=FONTS["title"], 
            anchor="center"
        )
        style.configure(
            "HeaderEmoji.TLabel",
            font=FONTS["emoji_large"],
            anchor="center"
        )
    
    def _create_widgets(self):
        self.pack_propagate(False)
        
        container = ttk.Frame(self)
        container.pack(expand=True, fill="both", pady=10)
        
        # Title label
        title = ttk.Label(
            container,
            text="EMILY'S TRANSCRIPTOR",
            style="HeaderTitle.TLabel"
        )
        title.pack()
        
        # Emoji label
        emoji = ttk.Label(
            container,
            text="🎥",
            style="HeaderEmoji.TLabel"
        )
        emoji.pack()
        
        # Set minimum size to prevent cutting
        self.update_idletasks()
        self.config(height=title.winfo_reqheight() + emoji.winfo_reqheight() + 20)