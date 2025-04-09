from tkinter import messagebox
from threading import Thread



class AsyncTaskManager:
    def __init__(self, gui_queue, control, finish):
        self.gui_queue = gui_queue
        self.control = control
        self.finish = finish
    
    def get_busy(self, path):
        """Execute video processing in background thread"""
        def task(control, finish):
            try:
                control.process_video(path)
                self.gui_queue.put(lambda: self._show_success())

            except Exception as e:
                self.gui_queue.put(lambda e=e: self._show_error(e))
                
            finally:
                finish()
        
        Thread(target=task, args=(self.control, self.finish), daemon=True).start()

    def _show_success(self):
        messagebox.showinfo("Success", "Transcription saved successfully!")
    
    def _show_error(self, error):
        messagebox.showerror("Error", str(error))