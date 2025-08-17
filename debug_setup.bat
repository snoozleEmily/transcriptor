@echo off
setlocal enabledelayedexpansion
title Emily's Transcriptor - Setup

set DEBUG=1

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

goto :main

:: ==================================================
:: Function :display
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
:: Function: check_python_version
:: ==================================================
:check_python_version
python --version 2>nul | findstr /r /c:"Python 3\.10\." >nul
exit /b %errorlevel%

:: ==================================================
:: MAIN SCRIPT
:: ==================================================
:main
call :display "Initializing Setup..."

:: ==================================================
:: Step 1: Check for Python 3.10
:: ==================================================
call :display "Step 1/8: Checking Python 3.10.x..."
call :check_python_version
if %errorlevel% == 0 (
    call :display "Python 3.10.x is already installed :)"
    set "PYTHON_CMD=python"
    goto :python_ok
)

:: ==================================================
:: Step 1.5: Check for any Python
:: ==================================================
python --version >nul 2>nul
if %errorlevel% == 0 (
    call :display "Another Python version detected. Will use pip for dependencies."
    set "PYTHON_CMD=python"
    goto :python_ok
)

:: ==================================================
:: Step 1.6: Check for winget
:: ==================================================
where winget >nul 2>nul
if errorlevel 1 (
    echo ERROR: No Python detected and winget not found.
    echo Please install Python 3.10 manually or install winget from Microsoft Store.
    pause
    exit /b 1
)

:: ==================================================
:: Step 1.7: Install Python 3.10 via winget
:: ==================================================
call :display "Installing Python 3.10 via winget..."
winget install --id Python.Python.3.10 -e --source winget --silent
if errorlevel 1 (
    call :handle_error "Python installation via winget failed"
)

:: ==================================================
:: Step 1.8: Handle user-scope installation and PATH
:: ==================================================
:: Check default user-scope install location
set "PYTHON_DIR=%LOCALAPPDATA%\Programs\Python\Python310"
if exist "%PYTHON_DIR%\python.exe" (
    set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%"
    set "PYTHON_CMD=python"
    echo Python found at %PYTHON_DIR%, added to PATH.
) else (
    :: Fallback to py launcher
    where python >nul 2>nul
    if errorlevel 1 (
        set "PYTHON_CMD=py -3.10"
        echo Python not in PATH, using py launcher.
    ) else (
        set "PYTHON_CMD=python"
    )
)

set "PYTHON_CMD=python"

:python_ok
:: Verify installation
call :check_python_version
if errorlevel 1 (
    call :handle_error "Python 3.10.x not found after installation"
)
call :display "Python 3.10 ready!"

:: ==================================================
:: Step 2: Check FFmpeg
:: ==================================================
call :display "Step 2/8: Checking FFmpeg..."
where ffmpeg >nul 2>nul
if %errorlevel% == 0 (
    call :display "FFmpeg is already installed :)"
    goto :ffmpeg_ok
)

:: ==================================================
:: Step 2.1: Try installing FFmpeg via winget
:: ==================================================
where winget >nul 2>nul
if %errorlevel% == 0 (
    call :display "Attempting to install FFmpeg via winget..."
    winget install --id Gyan.FFmpeg -e --source winget --scope user --accept-package-agreements --accept-source-agreements > winget_ffmpeg.log 2>&1
    set "WG_EXIT=%ERRORLEVEL%"
    type winget_ffmpeg.log
    if "%WG_EXIT%" == "0" (
        call :display "FFmpeg installed via winget!"
        goto :ffmpeg_ok
    ) else (
        echo Winget installation failed, exit code: %WG_EXIT%
        echo Will attempt manual download...
    )
) else (
    echo winget not found, will attempt manual download...
)

:: ==================================================
:: Step 2.2: Manual download fallback
:: ==================================================
set "ARCH=64"
if "%PROCESSOR_ARCHITECTURE%"=="x86" (
    if not defined PROCESSOR_ARCHITEW6432 set "ARCH=32"
)
set "FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win%ARCH%-gpl.zip"

call :display "Downloading FFmpeg manually..."
curl -L -o "%~dp0ffmpeg.zip" "%FFMPEG_URL%"
if errorlevel 1 (
    echo ERROR: Failed to download FFmpeg manually.
    echo Please install winget and try again, or manually install FFmpeg from https://ffmpeg.org/download.html
    pause
    exit /b 1
)

if not exist "%~dp0ffmpeg.zip" (
    echo ERROR: FFmpeg zip not found after download.
    pause
    exit /b 1
)

call :display "Extracting FFmpeg..."
powershell -Command "Expand-Archive -LiteralPath '%~dp0ffmpeg.zip' -DestinationPath '%~dp0.ffmpeg' -Force"
if errorlevel 1 (
    echo ERROR: Failed to extract FFmpeg.
    pause
    exit /b 1
)

del "%~dp0ffmpeg.zip" 2>nul
set "PATH=%~dp0.ffmpeg\bin;%PATH%"
call :display "FFmpeg ready!"

:ffmpeg_ok

:: ==================================================
:: Step 3: Create virtual environment
:: ==================================================
call :display "Step 3/8: Creating virtual environment..."
if not exist "venv" (
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 call :handle_error "Creating Python venv"
)

:: ==================================================
:: Step 4: Activate virtual environment
:: ==================================================
call :display "Step 4/8: Activating virtual environment..."
call venv\Scripts\activate.bat
if errorlevel 1 call :handle_error "Activating virtual environment"

:: ==================================================
:: Step 5: Install requirements
:: ==================================================
if exist requirements.txt (
    call :display "Step 5/8: Installing dependencies..."
    pip install -r requirements.txt
    if errorlevel 1 call :handle_error "Installing Python dependencies"
) else (
    call :display "requirements.txt not found. Skipping..."
)

:: ==================================================
:: Step 6: Install PyTorch
:: ==================================================
call :display "Step 6/8: Installing PyTorch..."
pip install torch==2.0.0 --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 call :handle_error "Installing PyTorch"

:: ==================================================
:: Step 7: Install llama_cpp
:: ==================================================
call :display "Step 7/8: Installing llama-cpp-python..."
pip install llama-cpp-python==0.3.9
if errorlevel 1 call :handle_error "Installing llama-cpp-python"

:: ==================================================
:: Step 8: Run main.py
:: ==================================================
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
