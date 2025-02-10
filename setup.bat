@echo off
echo ===========================================
echo  Setting up the Environment for Transcription
echo ===========================================

:: Step 1: Check if FFmpeg is installed and in PATH
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: FFmpeg is not installed or not added to PATH.
    echo -------------------------------------------
    echo Follow these steps to install and add FFmpeg to PATH:
    echo 1. A browser window will open to download FFmpeg.
    echo 2. Extract the files to a folder (e.g., C:\ffmpeg).
    echo 3. The System Environment Variables window will open.
    echo 4. Add the following path to the "Path" variable under "System Variables":
    echo    C:\ffmpeg\bin
    echo 5. Click OK, close the window, and restart your terminal.
    echo 6. Rerun this script after compl
    eting the steps.
    echo -------------------------------------------

    :: Open FFmpeg download page
    start https://ffmpeg.org/download.html

    :: Open System Environment Variables window
    rundll32 sysdm.cpl,EditEnvironmentVariables

    echo ===========================================
    echo  Please complete the above steps, then restart your terminal.
    echo  After that, rerun this script.
    echo ===========================================
    exit /b
)

:: Step 2: Check for Python Installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed.
    echo Download and install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    exit /b
)

:: Step 3: Upgrade pip to the latest version
echo Upgrading pip...
python -m pip install --upgrade pip

:: Step 4: Install dependencies from requirements.txt
if exist requirements.txt (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo ERROR: requirements.txt not found!
    echo Ensure it exists in the project directory and run the script again.
    exit /b
)

echo ===========================================
echo  Setup Complete! You can now run your script.
echo ===========================================
exit /b
