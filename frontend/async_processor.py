from tkinter import messagebox
from threading import Thread



class AsyncTaskManager:
    def __init__(self, gui_queue):
        self.gui_queue = gui_queue
    
    def process_video(self, path, control, finish):
        """Execute video processing in background thread"""
        def task():
            try:
                def progress(percentage):
                    # Send progress updates to the GUI queue
                    self.gui_queue.put(lambda: self._update_progress(percentage))
                
                control.process_video(path, progress)
                self.gui_queue.put(lambda: self._show_success())

            except Exception as e:
                # Capture 'e' as a default argument in the lambda
                self.gui_queue.put(lambda e=e: self._show_error(e))
                
            finally:
                finish()
        
        Thread(target=task, daemon=True).start()
    
    def _update_progress(self, percentage):
        print(f"Progress: {percentage}%")

    def _show_success(self):
        messagebox.showinfo("Success", "Transcription saved successfully!")
    
    def _show_error(self, error):
        messagebox.showerror("Error", str(error))

# ------------------ TESTING ------------------
if __name__ == "__main__":
    import queue
    import time 

    # Simulated control class with a process_video method
    class Control:
        def process_video(self, path, progress_callback):
            # Simulating progress from 0% to 100%
            for i in range(101):  
                progress_callback(i)
                time.sleep(0.1)  # Simulate processing delay

    # Simulated finish callback
    def finish():
        print("Processing finished.")

    # Create a GUI queue
    gui_queue = queue.Queue()

    # Create an instance of AsyncTaskManager
    manager = AsyncTaskManager(gui_queue)

    # Start processing video
    manager.process_video("dummy_path", Control(), finish)

    # Process GUI queue to handle updates
    while True:
        try:
            # Process tasks in the GUI queue
            task = gui_queue.get_nowait()
            task()  # Execute the task
        except queue.Empty:
            break