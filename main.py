import warnings
from src.errors.warnings_config import custom_warning
from src.frontend.interface import Interface
from src.utils.end_flow import EndFlow


# Protect sensitive path info
warnings.formatwarning = custom_warning

def main():
    flow = EndFlow()
    app = Interface(flow)
    app.mainloop()

if __name__ == "__main__":
    main()