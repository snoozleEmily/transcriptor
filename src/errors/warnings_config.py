import os
import warnings



def custom_warning(msg, *args, **kwargs):
    # Convert the full path to just the filename
    if len(args) > 2 and args[2]:  # Check if filename exists
        args = list(args)
        args[2] = os.path.basename(str(args[2]))
    return str(msg) + '\n'

warnings.formatwarning = custom_warning