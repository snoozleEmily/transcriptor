class Debug:
    """Holds runtime state flag for debbuging logs."""
    def __init__(self):
        self.dev_logs_fl = False

    def enable_dev_logs(self):
        self.dev_logs_fl = True

    def disable_dev_logs(self):
        self.dev_logs_fl = False

    def is_dev_logs_enabled(self):
        return self.dev_logs_fl

debug = Debug() # It should be one instance only
