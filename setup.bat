@echo off
setlocal enabledelayedexpansion
title Emily's Transcriptor - Setup

:: Hide command outputs by default
if not defined DEBUG (
    >nul 2>&1 (
        echo >nul
    )
)

:: Set colors (green text on black background)
color 0A 

:: ==================================================
:: Initial credits message
:: ==================================================
echo.
echo ==================================================
echo  Emily's Transcriptor
echo ==================================================
echo.
echo This is an independent project by Emily A. (@snoozleEmily)
echo You can download it from https://github.com/snoozleEmily/transcriptor
echo It is licensed under the GPL-3.0 license.
echo See README.md for more details.
echo.
echo ------------------------------------------------
echo.
echo Este e um projeto independente criado por Emily A. (@snoozleEmily)
echo Voce pode baixa-lo em https://github.com/snoozleEmily/transcriptor
echo Ele esta licenciado sob a licenca GPL-3.0.
echo Consulte o README.md para mais informacoes.
echo.
echo ==================================================
echo Now, let's get started! / Agora, vamos comecar!
echo ==================================================
timeout /t 5 /nobreak >nul
cls

:: Jump to MAIN to avoid accidentally running functions
goto :main

:: ==================================================
:: Function :display
:: Displays a message in a box
:: ==================================================
:display
echo.
echo ===========================================
echo  %~1
echo ===========================================
echo.
timeout /t 2 /nobreak >nul
goto :eof

:: ==================================================
:: Function :handle_error
:: Displays an error message and pauses
:: ==================================================
:handle_error
echo.
echo ===========================================================
echo ERROR encountered at step: %~1
echo ===========================================================
echo.
pause
exit /b 1

:: ==================================================
:: MAIN SCRIPT
:: ==================================================
:main
call :display "Initializing Setup..."

:: ==================================================
:: Step 1: Check for Python 3.10+
:: ==================================================
call :display "Step 1/8: Checking Python..."
where python >nul 2>nul
if errorlevel 1 (
    call :display "Python not found. Installing..."
    curl -L -o python.exe https://www.python.org/ftp/python/3.10.13/python-3.10.13-amd64.exe
    if errorlevel 1 call :handle_error "Downloading Python"
    start /wait python.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    if errorlevel 1 call :handle_error "Installing Python"
    del python.exe
) else (
    call :display "Python is already installed :)"
)
set "PYTHON_CMD=python"

:: ==================================================
:: Step 2: Check for Git
:: ==================================================
call :display "Step 2/8: Checking Git..."
where git >nul 2>nul
if errorlevel 1 (
    call :display "Git not found. Installing..."
    curl -L -o git.exe https://github.com/git-for-windows/git/releases/latest/download/Git-2.45.2-64-bit.exe
    if errorlevel 1 call :handle_error "Downloading Git"
    start /wait git.exe /VERYSILENT /NORESTART
    if errorlevel 1 call :handle_error "Installing Git"
    del git.exe
) else (
    call :display "Git is already installed :)"
)

:: ==================================================
:: Step 6: Check for FFmpeg
:: ==================================================
call :display "Step 6/8: Checking FFmpeg..."
where ffmpeg >nul 2>nul
if errorlevel 1 (
    call :display "FFmpeg not found. Installing..."
    curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
    mkdir .ffmpeg
    tar -xf ffmpeg.zip -C .ffmpeg
    move .ffmpeg\ffmpeg-master-latest-win64-gpl\* .ffmpeg >nul
    rmdir /s /q .ffmpeg\ffmpeg-master-latest-win64-gpl
    del ffmpeg.zip
    set "PATH=%~dp0.ffmpeg\bin;%PATH%"
) else (
    call :display "FFmpeg is already installed :)"
)

:: ==================================================
:: Step 7: Python environment setup
:: ==================================================
call :display "Step 7/8: Setting up Python environment..."

:: Step 7.1 - Create virtual environment
if not exist "venv" (
    call :display "Step 7.1/8: Creating virtual environment..."
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 call :handle_error "Creating Python venv"
)

:: Step 7.2 - Activate virtual environment
call :display "Step 7.2/8: Activating virtual environment..."
call venv\Scripts\activate.bat

:: Step 7.3 - Install requirements
if exist requirements.txt (
    call :display "Step 7.3/8: Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if errorlevel 1 call :handle_error "Installing Python dependencies"
) else (
    call :display "requirements.txt not found. Skipping..."
)

:: Step 7.4 - Install PyTorch
call :display "Step 7.4/8: Installing PyTorch..."
%PYTHON_CMD% -m pip install torch==2.0.0 --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 call :handle_error "Installing PyTorch"

:: Step 7.5 - Install llama_cpp
call :display "Step 7.5/8: Installing llama-cpp-python..."
%PYTHON_CMD% -m pip install llama-cpp-python==0.3.9
if errorlevel 1 call :handle_error "Installing llama-cpp-python"

:: ==================================================
:: Step 8: Run main.py
:: ==================================================
call :display "Step 8/8: Running Emily's Transcriptor..."
%PYTHON_CMD% -c "from main import main; main()"
if errorlevel 1 call :handle_error "Running main.py"

:: ==================================================
:: Final message
:: ==================================================
echo.
echo ===========================================
echo  All Done! Emily's Transcriptor is running
echo ===========================================
echo.
echo ------------------------------------------------
echo.
echo  (Press any key to close this window)
pause >nul
endlocal
exit /b 0
