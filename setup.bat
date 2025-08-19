:: NOT READY FOR USAGE - WORK IN PROGRESS
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
timeout /t 1 /nobreak >nul
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
:: Step 0: Check for winget
:: ==================================================
call :display "Step 0: Checking for winget..."
where winget >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Winget not found.
    echo [ACTION REQUIRED] Please install Python 3.10 manually:
    echo   https://www.python.org/downloads/release/python-31013/
    echo Or install winget from Microsoft Store and re-run this script.
    pause
    exit /b 1
)

:: ==================================================
:: Step 1: Check for Python 3.10
:: ==================================================
call :display "Step 1/8: Checking Python 3.10.x..."
call :check_python_version
if %errorlevel% == 0 (
    echo Python 3.10.x detected in PATH.
    set "PYTHON_CMD=python"
    echo Skipping Python installation.
    goto :python_ok
)

:: ==================================================
:: Step 1.2: Check for any Python
:: ==================================================
call :display "Step 1.2: Checking for any installed Python..."
python --version >nul 2>nul
if %errorlevel% == 0 (
    echo Another Python version detected.
    echo Will continue using existing Python for dependencies.
    set "PYTHON_CMD=python"
    goto :python_ok
) else (
    echo [WARN] No Python installation detected on this system.
)


:: ==================================================
:: Step 1.4: Install Python 3.10 via winget
:: ==================================================
call :display "Step 1.4: Installing Python 3.10 via winget..."
winget install --id Python.Python.3.10 -e --source winget
if errorlevel 1 (
    call :handle_error "Python installation via winget failed"
)

:: Reset color
color 0A

:: ==================================================
:: Step 1.5: Handle user-scope installation and PATH
:: ==================================================
call :display "Step 1.5: Adjusting PATH and verifying Python..."
set "PYTHON_DIR=%LOCALAPPDATA%\Programs\Python\Python310"
if exist "%PYTHON_DIR%\python.exe" (
    echo Python found at %PYTHON_DIR%
    set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%"
    set "PYTHON_CMD=python"
    :: Add permanently
    setx PATH "%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        set "PYTHON_CMD=py -3.10"
        echo Using Python launcher instead: py -3.10
    ) else (
        set "PYTHON_CMD=python"
        echo Python added to PATH automatically.
    )
)

:python_ok
call :check_python_version
if errorlevel 1 (
    call :handle_error "Python 3.10.x not found after installation"
)
call :display "Python 3.10 is ready to use!"

:: ==================================================
:: Step 1.4: Upgrade pip
:: ==================================================
call :display "Upgrading pip..."
python -m pip install --upgrade pip
if errorlevel 1 call :handle_error "Upgrading pip failed"


:: ==================================================
:: Step 2: Check FFmpeg
:: ==================================================
call :display "Step 2/8: Checking FFmpeg..."
where ffmpeg >nul 2>nul
if %errorlevel% == 0 (
    echo FFmpeg already available in PATH.
    echo Skipping FFmpeg installation.
    goto :ffmpeg_ok
) else (
    echo [WARN] FFmpeg not detected on this system.
)

:: ==================================================
:: Step 2.1: Try installing FFmpeg via winget
:: ==================================================
call :display "Step 2.1: Trying to install FFmpeg via winget..."
where winget >nul 2>nul
if %errorlevel% == 0 (
    winget install --id Gyan.FFmpeg -e --scope user --accept-package-agreements --accept-source-agreements
    set "WG_EXIT=%ERRORLEVEL%"
    if "%WG_EXIT%"=="0" (
        echo Winget successfully installed FFmpeg.
        goto :ffmpeg_ok
    ) else (
        echo [ERROR] Winget FFmpeg install failed with exit code %WG_EXIT%.
        echo Falling back to manual download.
    )
) else (
    echo [WARN] winget not found. Will attempt manual FFmpeg installation...
)

:: ==================================================
:: Step 2.2: Manual download fallback
:: ==================================================
call :display "Step 2.2: Downloading and extracting FFmpeg..."
set "ARCH=64"
if "%PROCESSOR_ARCHITECTURE%"=="x86" (
    if not defined PROCESSOR_ARCHITEW6432 set "ARCH=32"
)
set "FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win%ARCH%-gpl.zip"

curl -L -o "%~dp0ffmpeg.zip" "%FFMPEG_URL%"
if errorlevel 1 (
    echo [ERROR] Failed to download FFmpeg manually.
    echo [ACTION REQUIRED] Please install winget or download FFmpeg manually:
    echo   https://ffmpeg.org/download.html
    pause
    exit /b 1
)

powershell -Command "Expand-Archive -LiteralPath '%~dp0ffmpeg.zip' -DestinationPath '%~dp0.ffmpeg' -Force"
if errorlevel 1 (
    call :handle_error "Failed to extract FFmpeg"
)

del "%~dp0ffmpeg.zip" 2>nul
set "PATH=%~dp0.ffmpeg\bin;%PATH%"
:: Add FFmpeg permanently to PATH
setx PATH "%~dp0.ffmpeg\bin;%PATH%"
echo FFmpeg successfully installed locally.

:ffmpeg_ok
call :display "FFmpeg is ready to use!"

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
:: Step 5: Install CMake
:: ==================================================
call :display "Step 6/8: Installing CMake via winget..."
where winget >nul 2>nul
if %errorlevel% == 0 (
    winget install Kitware.CMake -e --accept-package-agreements --accept-source-agreements
    if errorlevel 1 call :handle_error "CMake installation failed"
    color 0A
) else (
    echo winget not found. Please install CMake manually.
)

:: ==================================================
:: Step 6: Install Visual Studio Build Tools
:: ==================================================
call :display "Step 7/8: Installing Visual Studio Build Tools via winget..."
where winget >nul 2>nul
if %errorlevel% == 0 (
    winget install Microsoft.VisualStudio.2022.BuildTools -e --accept-package-agreements --accept-source-agreements
    if errorlevel 1 call :handle_error "Visual Studio Build Tools installation failed"
    color 0A
) else (
    echo winget not found. Please install Visual Studio Build Tools manually.
)

:: ==================================================
:: Step 7: Install requirements
:: ==================================================
if exist requirements.txt (
    call :display "Step 5/8: Installing dependencies..."
    pip install -r requirements.txt
    if errorlevel 1 call :handle_error "Installing Python dependencies"
) else (
    call :display "requirements.txt not found. Skipping..."
)

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
