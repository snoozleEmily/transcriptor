import time
import webbrowser
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox



class TranscriptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emily's Transcriptor")
        self.root.geometry("550x350")
        self.root.configure(bg="#1a1a2f")
        self.root.resizable(False, False)
        self.progress_running = False

        # Use Courier New as the default font
        self.custom_font = ("Courier New", 10)
        self.title_font = ("Courier New", 16)

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('alt')
        
        self.style.configure('TLabel', 
                             background="#1a1a2f", 
                             foreground="white",
                             font=self.custom_font)
        
        self.style.configure('TButton', 
                             background="#2a2a4a", 
                             foreground="white",
                             borderwidth=0,
                             focuscolor="#1a1a2f",
                             font=self.custom_font,
                             relief="flat",
                             width=20)
        # Set hover effects: change background to gold yellow and font to black when active
        self.style.map('TButton', 
                       background=[('active', '#ffd700')],
                       foreground=[('active', 'black')])

        self.style.configure("Horizontal.TProgressbar",
                             background="#3a3a6a",
                             troughcolor="#1a1a2f",
                             thickness=10)

        self.main_frame = tk.Frame(self.root, bg="#1a1a2f")
        self.main_frame.pack(expand=True, fill='both', padx=40, pady=50)
        
        title_label = tk.Label(
            self.main_frame,
            text="EMILY'S TRANSCRIPTOR",
            font=self.title_font,
            bg="#1a1a2f",
            fg="white"
        )
        title_label.pack(pady=(0, 5))
        
        emoji_label = tk.Label(
            self.main_frame,
            text="🎥",
            font=("Segoe UI Emoji", 64),
            bg="#1a1a2f",
            fg="white"
        )
        emoji_label.pack(pady=(0, 35))
        
        buttons_frame = tk.Frame(self.main_frame, bg="#1a1a2f")
        buttons_frame.pack(pady=(0, 15))

        self.select_button = ttk.Button(
            buttons_frame,
            text="SELECT VIDEO",
            command=self.select_video
        )
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.github_button = ttk.Button(
            buttons_frame,
            text="GITHUB REPO",
            command=self.open_github
        )
        self.github_button.pack(side=tk.LEFT, padx=5)

        self.progress_frame = tk.Frame(self.main_frame, bg="#1a1a2f")
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="Processing: 0%",
            style='TLabel'
        )
        self.progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate',
            style="Horizontal.TProgressbar"
        )
        self.progress_bar.pack()

    def select_video(self):
        if self.progress_running:
            messagebox.showinfo("Already Running", "A video is already being processed!")
            return

        file_path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )
        if file_path:
            self.progress_frame.pack(pady=10)
            self.progress_running = True
            threading.Thread(target=self.simulate_processing, daemon=True).start()

    def simulate_processing(self):
        for i in range(101):
            if not self.progress_running:
                break
            self.progress_bar['value'] = i
            self.progress_label.config(text=f"Processing: {i}%")
            time.sleep(0.05)
            self.root.update_idletasks()
        
        self.progress_running = False
        self.progress_frame.pack_forget()
        messagebox.showinfo("Complete", "Video processing completed!")

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
