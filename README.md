# Emily's Transcriptor [WIP]

Do you need to turn a video into text or want to get organized notes from a lengthy video? This app does that for you absolutely for free!

---
> 🇧🇷 Oieee! Precisa dessas explicações em pt-BR? Me chama que te ajudo! 📚✨
> 🇪🇸 ¡Holaa! ¿Necesitas esta explicación en español? ¡Llámame! 🔥📖
> 🇮🇹 Ciao! Hai bisogno di questa spiegazione in ITA? Chiamami! 🍕📜
> 🇫🇷 Coucou! Vous voulez cette explication en français? Appelez-moi! 🥖📚
> 🇷🇴 Hei! Ai nevoie de această explicație în română? Sună-mă! 🏛️📖
---
## Usage

The goal of this app is to make it easy and fun for everyone to use, even if you have no technical background.

---

### **For Non-Techies** 
1. Download the project files from github.
2. Open the folder and click on the file that ends with `.exe`. 
3. Click on the button `Select Video` and choose the one you'd like.

---

### **For Developers**

#### **Windows Users**
If you're on Windows, simply run `setup.bat`. The script will handle all the dependencies and setup configurations for you.

---

#### **Other Operating Systems**
If you're working on a different operating system, follow these steps:

1. **Install Python and Git**:
   - [Python](https://www.python.org/downloads/)
   - [Git](https://git-scm.com/downloads)

2. **Install FFmpeg**:
   - Download [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip).
   - Add FFmpeg to your system's `PATH`.

3. **Clone the Repository**:
   Copy the repository to your machine:
   ```bash
   git clone https://github.com/snoozleEmily/transcriptor
   ```

4. **Set Up the Virtual Environment**:
   - Navigate to the root folder of the repository:
     ```bash
     cd <repository-folder>
     ```
   - Activate the virtual environment:
     ```bash
     venv\Scripts\activate.bat  # Windows
     ```
     ```bash
     source venv/bin/activate   # macOS/Linux
     ```

5. **Install Dependencies**:
   Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
  
6.  [there is another step to add for version 2 - how to setup pydub]

7. **Run the Script**:
   You're ready to go! Run the script with:
   ```bash
   python main.py
   ```
---

## Contributing

**Contributions are welcome!** Below are some guidelines to help you get started:
[WIP]

---

## License

This project is licensed under the GNU General Public License. This means you are free to build upon the current code to develop the app further, but you **must credit the original author** and distribute any modifications under the **same license**. For more details, see the [license file](LICENSE).
