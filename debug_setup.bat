@echo off
setlocal enabledelayedexpansion
title Emily's Transcriptor - Setup

:: Enable debug output
set DEBUG=1

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

:: Jump to MAIN
goto :main

:: ==================================================
:: Display a message in a box
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
:: Handle errors
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
:: Check Python 3.10.x
:: ==================================================
:check_python_version
python --version
if errorlevel 1 (
    echo Python not found
    exit /b 1
)
python --version | findstr /r /c:"Python 3\.10\." >nul
exit /b %errorlevel%

:: ==================================================
:: MAIN SCRIPT
:: ==================================================
:main
call :display "Initializing Setup..."

:: Step 1: Check Python
call :display "Step 1/8: Checking Python 3.10.x..."
call :check_python_version
if %errorlevel% == 0 (
    call :display "Python 3.10.x is already installed :)"
    set "PYTHON_CMD=python"
    goto :python_ok
)

:: ==================================================
:: Step 1.5: Architecture check and Python download
:: ==================================================
set "ARCH=64"
if "%PROCESSOR_ARCHITECTURE%"=="x86" (
    if not defined PROCESSOR_ARCHITEW6432 set "ARCH=32"
)

:: Base URL for Python 3.10.13
set "PYTHON_BASE_URL=https://www.python.org/ftp/python/3.10.13/python-3.10.13"

:: Append architecture-specific suffix
if "%ARCH%"=="64" (
    set "PYTHON_URL=%PYTHON_BASE_URL%-amd64.exe"
) else (
    set "PYTHON_URL=%PYTHON_BASE_URL%.exe"
)

set "PYTHON_INSTALLER=python_installer.exe"

:: Show the URL we are downloading
echo Downloading Python from: %PYTHON_URL%

:: Download using curl
curl -L -o "%PYTHON_INSTALLER%" "%PYTHON_URL%"
if errorlevel 1 (
    call :handle_error "Failed to download Python installer"
)

:: Install Python (logs progress)
call :display "Installing Python 3.10..."
:: Run installer directly, not via start
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 /log python_install.log
if errorlevel 1 (
    echo See python_install.log for details
    call :handle_error "Python installation failed"
)
del "%PYTHON_INSTALLER%" 2>nul
set "PYTHON_CMD=python"

:: Step 2: FFmpeg
call :display "Step 2/8: Checking FFmpeg..."
where ffmpeg
if %errorlevel% == 0 (
    call :display "FFmpeg is already installed :)"
    goto :ffmpeg_ok
)

:: Download FFmpeg
set "FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win%ARCH%-gpl.zip"
call :display "Downloading FFmpeg..."
curl -L -o ffmpeg.zip "%FFMPEG_URL%"
if errorlevel 1 call :handle_error "Failed to download FFmpeg"

:: Extract FFmpeg
call :display "Extracting FFmpeg..."
mkdir .ffmpeg 2>nul
powershell -command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.ffmpeg'"
if errorlevel 1 call :handle_error "Failed to extract FFmpeg"
del ffmpeg.zip 2>nul
set "PATH=%~dp0.ffmpeg\bin;%PATH%"

:ffmpeg_ok

:: Step 3: Create virtual environment
call :display "Step 3/8: Creating virtual environment..."
if not exist "venv" (
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 call :handle_error "Creating Python venv"
)

:: Step 4: Activate virtual environment
call :display "Step 4/8: Activating virtual environment..."
call venv\Scripts\activate.bat
if errorlevel 1 call :handle_error "Activating virtual environment"

:: Step 5: Install requirements
if exist requirements.txt (
    call :display "Step 5/8: Installing dependencies..."
    pip install -r requirements.txt --verbose
    if errorlevel 1 call :handle_error "Installing Python dependencies"
) else (
    call :display "requirements.txt not found. Skipping..."
)

:: Step 6: Install PyTorch
call :display "Step 6/8: Installing PyTorch..."
pip install torch==2.0.0 --index-url https://download.pytorch.org/whl/cpu --verbose
if errorlevel 1 call :handle_error "Installing PyTorch"

:: Step 7: Install llama_cpp
call :display "Step 7/8: Installing llama-cpp-python..."
pip install llama-cpp-python==0.3.9 --verbose
if errorlevel 1 call :handle_error "Installing llama-cpp-python"

:: Step 8: Run main.py
call :display "Step 8/8: Running Emily's Transcriptor..."
python -c "from main import main; main()"
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