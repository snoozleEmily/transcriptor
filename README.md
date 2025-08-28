# Emily's Transcriptor

Do you need to turn a video into text or want to get organized notes from a lengthy video? This app does that for you — absolutely free!

`NOTE: THIS APP IS STILL IN DEVELOPMENT.`

## Usage

The goal of this app is to make it easy and fun for everyone to use, even if you have no technical background.

### **Steps**
1. Download the project files from GitHub.
2. Open the folder and run the file that ends with `.exe`. [not available yet]
3. Click the button `Select Video` and choose the one you'd like to transcribe.

---

## Contributing [WIP]

**Contributions are welcome!** Below are some guidelines to help you get started:

#### **Windows Users**
If you're on Windows, simply run `setup.bat`.  
The script will handle all tools and setup configurations required.  
[⚠ This script is a work in progress and not ready yet.]

#### **Other Operating Systems**
If you're working on a different operating system `or want to manually arrange your setup`, follow these steps:

1. **Install Python and Git**:
   - For best compatibility, use Python 3.10: [Python 3.10](https://www.python.org/downloads/)
   - Install Git: [Git](https://git-scm.com/downloads)

2. **Install FFmpeg** *(required by PyTorch and audio processing)*:
   - Download [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip).
   - Add FFmpeg to your system `PATH`.

3. **Clone the Repository**:
   Copy the repository to your machine:
   ```bash
   git clone https://github.com/snoozleEmily/transcriptor
   ```

4. **Set Up and Activate the Virtual Environment**:
   - Navigate to the root folder of the repository:
     ```bash
     cd <repository-folder>
     ```
   - Create the virtual environment (if not already created):
     ```bash
     python -m venv venv
     ```
   - Activate it:
     ```bash
     source venv/bin/activate   # macOS/Linux
     ```
     ```bash
     venv\Scripts\activate      # Windows
     ```

5. **Install CMake** *(required for Llama)*:
   - Download [CMake](https://cmake.org/download/) and follow the installation instructions for your OS.

6. **Install a C++ Compiler / Build Tools** *(required for Llama and C++ extensions)*:
   - On Windows, install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).  
   - On Linux/macOS, install `gcc` / `clang` via your package manager.

7. **Setup Required Corpora**:
    Download NLTK data for TextBlob:
   ```bash
   python -m textblob.download_corpora
   ```

8. **Install Dependencies**:
   Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

9. **Run the Script**:
   You're ready to go! Run the app with:
   ```bash
   python main.py
   ```

---

## License

This project is licensed under the GNU General Public License.  
This means you are free to build upon the current code to develop the app further, but you **must credit the original author** and distribute any modifications under the **same license**. For more details, see the [license file](LICENSE).

---
> 🇧🇷 Oieee! Precisa dessas explicações em pt-BR? Me chama que te ajudo! 📚✨  

> 🇪🇸 ¡Holaa! ¿Necesitas esta explicación en español? ¡Llámame! 🔥📖  

> 🇮🇹 Ciao! Hai bisogno di questa spiegazione in ITA? Chiamami! 🍕📜  

> 🇫🇷 Coucou! Vous voulez cette explication en français? Appelez-moi! 🥖📚  

> 🇷🇴 Hei! Ai nevoie de această explicație în română? Sună-mă! 🏛️📖  
---
