import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser

class TranscriptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcriptor")
        self.root.geometry("500x250")
        self.root.configure(bg="#2b2b2b")  # Dark background color
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('alt')
        self.style.configure('TLabel', background="#2b2b2b", foreground="white")
        self.style.configure('TButton', background="#3a3a3a", foreground="white", bordercolor="#4a4a4a")
        self.style.map('TButton', 
                      background=[('active', '#4a4a4a'), ('pressed', '#5a5a5a')])
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title Label
        title_label = ttk.Label(
            main_frame,
            text="Emily's Transcriptor",
            font=("Helvetica", 12)
        )
        title_label.pack(pady=(0, 10))
        
        # Emoji Label
        emoji_label = ttk.Label(
            main_frame,
            text="🎥",
            font=("Helvetica", 40)
        )
        emoji_label.pack(pady=(0, 20))
        
        # Select Video Button
        select_button = ttk.Button(
            main_frame,
            text="Select Video",
            width=18,
            command=self.select_video
        )
        select_button.pack(pady=(0, 10))
        
        # GitHub Button
        github_button = ttk.Button(
            main_frame,
            text="See Github Repo",
            width=14,
            command=self.open_github
        )
        github_button.pack(pady=(0, 10))

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