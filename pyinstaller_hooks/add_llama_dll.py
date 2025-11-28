# Runtime hook: register the extracted 
# llama_cpp/lib folder with Windows DLL search

import os
import sys



_meipass = getattr(sys, "_MEIPASS", None)  # set by PyInstaller in onefile mode
if _meipass:
    # expected path where llama_cpp's native libs will be extracted
    dll_dir = os.path.join(_meipass, "llama_cpp", "lib")

    if os.path.isdir(dll_dir):
        try:
            os.add_dll_directory(dll_dir)  # Windows only (Py >=3.8)

        except Exception as e:
            print(f"Path of dll_dir failed: {e}")
            # If this fails, continue — older Python/other platforms will ignore
            pass