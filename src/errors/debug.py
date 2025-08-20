class Debug:
    """Singleton-like flag manager for enabling/disabling developer debug logs."""

    def __init__(self):
        self.dev_logs_fl = False

    def enable_dev_logs(self) -> None:
        """Turn on developer debug logs."""
        self.dev_logs_fl = True

    def disable_dev_logs(self) -> None:
        """Turn off developer debug logs."""
        self.dev_logs_fl = False

    def is_dev_logs_enabled(self) -> bool:
        """Check if developer debug logs are enabled."""
        return self.dev_logs_fl

    def __repr__(self) -> str:
        return f"<Debug dev_logs_enabled={self.dev_logs_fl}>"

    def dprint(self, msg: str) -> None:
        """
        Prints a message with [DEBUG] prefix if DEV logs are enabled.
        """
        if self.dev_logs_fl:
            print(f"[DEBUG] {msg}")


# Global instance (single point of control)
debug = Debug()