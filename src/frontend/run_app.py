import logging
import traceback
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path


from src.utils.end_flow import EndFlow # Is it a good idea to call this here?
from src.frontend.interface import Interface
from src.logs.do_logging import (
    configure_logging,
    install_global_exception_hooks,
    log_unexpected_error,
)


def run_app(flow: EndFlow) -> None:
    # 1) configure logging early
    log_path = Path.home() / ".my_app" / "logs" / "app.log"
    configure_logging(log_level=logging.INFO, log_file=log_path)
    install_global_exception_hooks()

    # 2) create a hidden root to show modal error dialog if startup fails
    root = tk.Tk()
    root.withdraw()

    try:
        # Minimal init in __init__ and heavy init in initialize()
        app = Interface(flow)
        app.initialize()

    except Exception as exc:
        # Log full traceback (also caught by global hook, but log explicitly here too)
        logging.getLogger("startup").exception("Failed to initialize GUI")
        try:
            popup_seemore(root, exc)
        except Exception:
            # Fallback: standard messagebox if even our popup fails
            messagebox.showerror(
                "Startup error", "Failed to start the application. Check logs."
            )
        raise SystemExit(1)
    finally:
        # destroy the temporary root we used for dialogs
        try:
            root.destroy()
        except Exception:
            pass

    app.mainloop()


def popup_seemore(root, error: Exception):
    """
    Display a compact error dialog with optional 'See More' for traceback.
    Users can take a screenshot instead of copying.
    """
    tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))

    window = tk.Toplevel(root)
    window.title("An unexpected error occurred")
    window.resizable(False, False)

    # Friendly message
    label = tk.Label(
        window,
        text=(
            "Oops! Something went wrong.\n"
            "Please click on 'see more', take a screenshot, and open an issue on github."
        ),
        justify="left",
        padx=10,
        pady=10,
    )
    label.pack(fill="x")

    # Container for buttons
    btn_frame = tk.Frame(window)
    btn_frame.pack(fill="x", pady=(0, 10), padx=10)

    # See more / toggle button
    text_widget = tk.Text(window, height=15, width=70)
    text_widget.insert("1.0", tb)
    text_widget.config(state=tk.DISABLED)
    text_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    text_widget.pack_forget()  # hidden initially

    def toggle_traceback():
        if text_widget.winfo_viewable():
            text_widget.pack_forget()
            window.geometry("")
        else:
            text_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            window.geometry("")

    ttk.Button(btn_frame, text="See More", command=toggle_traceback).pack(side="left")
    ttk.Button(btn_frame, text="Close", command=window.destroy).pack(side="right")

    # Make modal
    window.transient(root)
    window.grab_set()
    root.wait_window(window)
