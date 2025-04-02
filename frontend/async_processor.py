from tkinter import messagebox
from threading import Thread



class AsyncTaskManager:
    def __init__(self, gui_queue):
        self.gui_queue = gui_queue
    
    def process_video(self, path, controller, completion_callback):
        """Execute video processing in background thread"""
        def task():
            try:
                controller.process_video(path)
                self.gui_queue.put(lambda: self._show_success())

            except Exception as e:
                self.gui_queue.put(lambda: self._show_error(e))
                
            finally:
                completion_callback()
        
        Thread(target=task, daemon=True).start()
    
    def _show_success(self):
        messagebox.showinfo("Success", "Transcription saved successfully!")
    
    def _show_error(self, error):
        messagebox.showerror("Error", str(error))