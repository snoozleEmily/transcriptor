import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser

class TranscriptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcriptor")
        self.root.geometry("550x300")  # Increased screen size
        self.root.configure(bg="#1a1a2f")  # Deep navy blue background
        self.root.resizable(False, False)

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('alt')
        
        # Configure colors and fonts
        self.style.configure('TLabel', 
                           background="#1a1a2f", 
                           foreground="white",
                           font=("Arial", 10))
        
        self.style.configure('TButton', 
                           background="#2a2a4a", 
                           foreground="white",
                           borderwidth=0,
                           focuscolor="#1a1a2f",
                           font=("Arial", 10, "bold"),
                           relief="flat")
        
        self.style.map('TButton', 
                     background=[('active', '#3a3a6a'), ('pressed', '#4a4a8a')],
                     foreground=[('active', 'white')])

        # Main container
        main_frame = tk.Frame(self.root, bg="#1a1a2f")
        main_frame.pack(expand=True, fill='both', padx=40, pady=30)
        
        # Title Label
        title_label = tk.Label(
            main_frame,
            text="Emily's Transcriptor",
            font=("Arial", 16, "bold"),
            bg="#1a1a2f",
            fg="white"
        )
        title_label.pack(pady=(0, 5))
        
        # Emoji Label (white icon with transparent background)
        emoji_label = tk.Label(
            main_frame,
            text="🎥",
            font=("Segoe UI Emoji", 64),  # Larger emoji size
            bg="#1a1a2f",
            fg="white"  # Set emoji color to white
        )
        emoji_label.pack(pady=(0, 15))
        
        # Select Video Button
        select_button = ttk.Button(
            main_frame,
            text="SELECT VIDEO",
            width=30,  
            command=self.select_video
        )
        select_button.pack(pady=(0, 15))  

        # GitHub Button
        github_button = ttk.Button(
            main_frame,
            text="GITHUB REPO",
            width=30,  # Adjusted width
            command=self.open_github
        )
        github_button.pack(pady=(0, 15))  # Adjusted pady to keep spacing reasonable


    def select_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )
        if file_path:
            # Process the selected video file here
            pass

    def open_github(self):
        webbrowser.open("https://github.com/snoozleEmily/transcriptor")
        messagebox.showinfo(
            "GitHub Repo",
            "Opening GitHub repository in your browser..."
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptorApp(root)
    root.mainloop()