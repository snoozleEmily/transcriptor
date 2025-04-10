import threading
from queue import Queue


class AsyncTaskManager:
    def __init__(self, gui_queue, view, completion_callback):
        self.gui_queue = gui_queue
        self.view = view  # Reference to Interface
        self.completion_callback = completion_callback
        
    def get_busy(self, path, progress_handler=None):
        """Handle async transcription with progress updates"""
        def task():
            try:
                result = self.view.controller.process_video(path)
                self.gui_queue.put(self.completion_callback)
            except Exception as e:
                self.gui_queue.put(lambda: self.view.show_error(str(e)))
                
        threading.Thread(target=task).start()