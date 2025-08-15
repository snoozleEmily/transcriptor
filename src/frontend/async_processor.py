import threading



class AsyncTaskManager:
    """
    Manages asynchronous video processing tasks to prevent blocking the GUI.

    Attributes:
        gui_queue: Queue for passing GUI update callbacks from worker threads to the main thread.
        interface: Reference to the Interface instance (main Tkinter window), used for error reporting
                   and accessing the flow object that handles the actual video processing.
        completion_callback: Function to call on the main thread when processing finishes.
    """

    def __init__(self, gui_queue, interface, completion_callback):
        self.gui_queue = gui_queue
        self.interface = interface
        self.completion_callback = completion_callback

    def get_busy(
        self, path, config_params=None, quick_script=False, progress_handler=None
    ):
        """
        Launches video processing in a separate thread to avoid freezing the GUI.

        Args:
            path (str): Path to the video file to process.
            config_params (ContentType, optional): Configuration parameters for processing.
            quick_script (bool, optional): If True, output a simplified txt file.
            progress_handler (callable, optional): Callback function to report progress updates.

        Notes:
            - The actual processing is delegated to `self.interface.flow.process_video`.
            - GUI updates (completion feedback or errors) are queued via `self.gui_queue`
              to ensure thread-safe interaction with Tkinter widgets.
            - Exceptions are caught and forwarded to the interface's `show_error` method.
        """

        def task():
            """
            Worker function running in a separate daemon thread.

            Executes video processing and ensures results are communicated back to the main GUI thread.
            """
            try:
                result = self.interface.flow.process_video(  # References EndFlow
                    path,
                    config_params=config_params,
                    quick_script=quick_script,
                    progress_callback=progress_handler,
                )

                # Schedule completion callback on the main GUI thread
                self.gui_queue.put(lambda: self.completion_callback(result))

            except Exception as e:
                # Schedule error display on the main GUI thread
                self.gui_queue.put(lambda: self.interface.show_error(str(e)))

        # Launch async thread; daemon ensures it exits with app
        threading.Thread(target=task, daemon=True).start()
