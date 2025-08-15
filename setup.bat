@echo off
setlocal enabledelayedexpansion
title Emily's Transcriptor - Setup
color 0A 

:: ------------------------------------------------------------
:: Initial Credits
:: ------------------------------------------------------------
echo.
echo ==================================================
echo  Emily's Transcriptor
echo ==================================================
echo This is an independent project by Emily A. (@snoozleEmily)
echo https://github.com/snoozleEmily/transcriptor
echo Licensed under GPL-3.0
echo.
timeout /t 3 /nobreak >nul
cls

:: ------------------------------------------------------------
:: Function: Display message
:: ------------------------------------------------------------
:display
echo.
echo ===========================================
echo  %~1
echo ===========================================
echo.
timeout /t 1 /nobreak >nul
goto :eof

:main
call :display "Initializing Setup..."

:: ------------------------------------------------------------
:: Step 1 - Install Git if missing
:: ------------------------------------------------------------
call :display "Step 1/8: Checking Git..."
where git >nul 2>nul || (
    call :display "Git not found. Installing..."
    curl -L -o git.exe https://github.com/git-for-windows/git/releases/latest/download/Git-2.45.2-64-bit.exe
    start /wait git.exe /VERYSILENT /NORESTART
    del git.exe
)

:: ------------------------------------------------------------
:: Step 2 - Install Python 3.10 if missing
:: ------------------------------------------------------------
call :display "Step 2/8: Checking Python 3.10..."
set "PYTHON_CMD=python"
for /f "tokens=2 delims= " %%v in ('python --version 2^>nul') do set PYTHON_VER=%%v
echo %PYTHON_VER% | findstr /r "^3\.10\." >nul || (
    call :display "Installing Python 3.10..."
    curl -L -o python.exe https://www.python.org/ftp/python/3.10.13/python-3.10.13-amd64.exe
    start /wait python.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    del python.exe
)

:: ------------------------------------------------------------
:: Step 3 - Install CMake if missing
:: ------------------------------------------------------------
call :display "Step 3/8: Checking CMake..."
where cmake >nul 2>nul || (
    call :display "CMake not found. Installing..."
    curl -L -o cmake.msi https://github.com/Kitware/CMake/releases/latest/download/cmake-3.29.0-windows-x86_64.msi
    start /wait msiexec /i cmake.msi /quiet /norestart
    del cmake.msi
)

:: ------------------------------------------------------------
:: Step 4 - C++ Compiler (install if missing)
:: ------------------------------------------------------------
call :display "Step 4/8: Checking C++ Compiler..."
where cl >nul 2>nul || (
    call :display "No C++ compiler detected. Installing Visual Studio Build Tools (C++ workload)..."
    set "VSBT_URL=https://aka.ms/vs/17/release/vs_BuildTools.exe"
    curl -L -o vs_buildtools.exe %VSBT_URL%
    start /wait vs_buildtools.exe --quiet --wait --norestart --nocache ^
        --add Microsoft.VisualStudio.Workload.VCTools ^
        --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 ^
        --add Microsoft.VisualStudio.Component.Windows10SDK.19041 ^
        --includeRecommended
    del vs_buildtools.exe
)

:: Re-check cl after install
where cl >nul 2>nul || (
    call :display "ERROR: C++ compiler still not available. Please reboot and re-run this script."
    goto :end
)

:: ------------------------------------------------------------
:: Step 5 - CUDA (optional, auto-install if NVIDIA GPU)
:: ------------------------------------------------------------
call :display "Step 5/8: Checking CUDA..."
where nvcc >nul 2>nul
if %errorlevel% neq 0 (
    for /f %%G in ('powershell -NoProfile -Command "(Get-CimInstance Win32_VideoController ^| Where-Object {$_.Name -match 'NVIDIA'} ^| Measure-Object).Count"') do set NVIDIA_COUNT=%%G
    if not defined NVIDIA_COUNT set NVIDIA_COUNT=0
    if %NVIDIA_COUNT% GTR 0 (
        call :display "NVIDIA GPU detected. Installing CUDA Toolkit..."
        set "CUDA_URL=https://developer.download.nvidia.com/compute/cuda/12.4.1/network_installers/cuda_12.4.1_windows_network.exe"
        curl -L -o cuda-installer.exe %CUDA_URL%
        start /wait cuda-installer.exe -s
        del cuda-installer.exe
    ) else (
        call :display "No NVIDIA GPU detected. Skipping CUDA install."
    )
) else (
    call :display "CUDA already installed."
)

:: ------------------------------------------------------------
:: Step 6 - Install FFmpeg if missing
:: ------------------------------------------------------------
call :display "Step 6/8: Checking FFmpeg..."
where ffmpeg >nul 2>nul || (
    call :display "Installing FFmpeg..."
    curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
    mkdir .ffmpeg
    tar -xf ffmpeg.zip -C .ffmpeg
    move .ffmpeg\ffmpeg-master-latest-win64-gpl\* .ffmpeg >nul
    rmdir /s /q .ffmpeg\ffmpeg-master-latest-win64-gpl
    del ffmpeg.zip

    :: Add FFmpeg to PATH for current session
    set "PATH=%~dp0.ffmpeg\bin;%PATH%"

    :: Persist FFmpeg PATH safely
    setx PATH "%PATH%;%~dp0.ffmpeg\bin"
)

:: ------------------------------------------------------------
:: Step 7 - Setup Python environment & dependencies
:: ------------------------------------------------------------
call :display "Step 7/8: Setting up Python environment..."

:: Step 7.1/8 - Create virtual environment if it doesn't exist
if not exist "venv" (
    call :display "Step 7.1/8: Creating Python virtual environment..."
    %PYTHON_CMD% -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip inside venv
python -m pip install --upgrade pip

:: Step 7.2/8 - Install dependencies from requirements.txt
if exist requirements.txt (
    call :display "Step 7.2/8: Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
) else (
    call :display "Step 7.2/8: requirements.txt not found!"
    echo Please place requirements.txt in this folder and re-run the script, OR install the packages manually.
)

:: Step 7.3/8 - Install PyTorch if missing
call :display "Step 7.3/8: Checking for PyTorch..."
python -c "import importlib.util,subprocess,sys; \
if importlib.util.find_spec('torch') is None: \
    subprocess.check_call([sys.executable,'-m','pip','install','torch==2.0.0','--index-url','https://download.pytorch.org/whl/cpu'])"

:: Step 7.4/8 - Install llama_cpp if missing
python -c "import importlib.util,subprocess,sys; \
import pkg_resources; \
try: \
    pkg_resources.require('llama-cpp-python==0.3.9'); \
except pkg_resources.DistributionNotFound: \
    subprocess.check_call([sys.executable,'-m','pip','install','llama-cpp-python==0.3.9'])"

:: ----------------- Step 8: Run main.py -----------------
call :display "Step 8/8: Starting Emily's Transcriptor..."
python -c "from main import main; main()"

:: Final message
echo.
echo ===========================================
echo  All Done! Happy Coding :D
echo ===========================================
echo.

echo ------------------------------------------------
echo.
echo  (Press any key to close this window)
pause >nul
:end
endlocal
