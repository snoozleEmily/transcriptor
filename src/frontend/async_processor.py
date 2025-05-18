import threading



class AsyncTaskManager:
    def __init__(self, gui_queue, interface, completion_callback):
        self.gui_queue = gui_queue
        self.interface = interface
        self.completion_callback = completion_callback

    def get_busy(self, path, config_params=None, pretty_notes=False, progress_handler=None):
        """Handle async transcription with progress updates
        
        Args:
            path: Path to the video file
            config_params: Content configuration parameters
            pretty_notes: Boolean flag for PDF/TXT output
            progress_handler: Callback for progress updates
        """
        def task():
            try:
                result = self.interface.controller.process_video(
                    path, 
                    config_params=config_params,
                    pretty_notes=pretty_notes,
                    progress_callback=progress_handler
                )
                self.gui_queue.put(lambda: self.completion_callback(result))

            except Exception as e:
                self.gui_queue.put(lambda: self.interface.show_error(str(e)))

        threading.Thread(target=task, daemon=True).start()