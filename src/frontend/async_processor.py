import threading



class AsyncTaskManager:
    def __init__(self, gui_queue, interface, completion_callback):
        self.gui_queue = gui_queue
        self.interface = interface
        self.completion_callback = completion_callback
        
    def get_busy(self, path, progress_handler=None):
        """Handle async transcription with progress updates"""
        def task():
            try:
                result = self.interface.controller.process_video(path)
                self.gui_queue.put(self.completion_callback)
            except Exception as e:
                self.gui_queue.put(lambda: self.interface.show_error(str(e)))
                
        threading.Thread(target=task).start()