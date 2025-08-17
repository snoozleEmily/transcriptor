@echo off
setlocal enabledelayedexpansion
title Emily's Transcriptor - Setup

:: ==================================================
:: Configuration Section (MODIFY THESE IF NEEDED)
:: ==================================================
set PYTHON_MIN_VERSION=3.10.0
set PYTHON_MAX_VERSION=3.10.99
set PYTHON_DOWNLOAD_VERSION=3.10.13
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_DOWNLOAD_VERSION%/python-%PYTHON_DOWNLOAD_VERSION%-amd64.exe
set PYTHON_URL_32BIT=https://www.python.org/ftp/python/%PYTHON_DOWNLOAD_VERSION%/python-%PYTHON_DOWNLOAD_VERSION%.exe
set FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
set FFMPEG_URL_32BIT=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win32-gpl.zip
set TORCH_VERSION=2.0.0
set LLAMA_CPP_VERSION=0.3.9

:: ==================================================
:: Initial Setup
:: ==================================================
if not defined DEBUG >nul 2>&1 echo off
color 0A

:: ==================================================
:: System Architecture Detection
:: ==================================================
set ARCH=64
if "%PROCESSOR_ARCHITECTURE%"=="x86" (
    if not defined PROCESSOR_ARCHITEW6432 set ARCH=32
)

:: ==================================================
:: Display Credits
:: ==================================================
echo.

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

:: ==================================================
:: Enhanced Functions
:: ==================================================
:display
echo.
echo ===========================================
echo  %~1
echo ===========================================
echo.
timeout /t 2 /nobreak >nul
goto :eof

:handle_error
echo.
echo ===========================================================
echo ERROR: %~1
echo ===========================================================
echo.
echo Debug Info:
echo Step: %~2
echo Errorlevel: %errorlevel%
echo Architecture: %ARCH%-bit
echo.
pause
exit /b 1

:check_python_version
for /f "tokens=2 delims= " %%A in ('python --version 2^>^&1') do (
    for /f "tokens=1-3 delims=." %%B in ("%%A") do (
        if %%B EQU 3 (
            if %%C EQU 10 (
                if %%D GEQ 0 (
                    exit /b 0
                )
            )
        )
    )
)
exit /b 1

:verify_python
python --version >nul 2>&1 || (
    call :handle_error "Python not found in PATH" "Python Check"
)
call :check_python_version || (
    call :handle_error "Python version must be between %PYTHON_MIN_VERSION% and %PYTHON_MAX_VERSION%" "Python Version Check"
)
goto :eof

:: ==================================================
:: Main Installation
:: ==================================================
call :display "Starting Installation (%ARCH%-bit system)..."

:: Step 1: Python Installation
call :display "Step 1/8: Checking Python..."
python --version >nul 2>&1 && call :check_python_version
if %errorlevel% equ 0 (
    call :display "Compatible Python 3.10.x found :)"
    goto :python_ok
)

set "PYTHON_INSTALLER=python_installer.exe"
call :display "Downloading Python %PYTHON_DOWNLOAD_VERSION% (%ARCH%-bit)..."
if %ARCH% equ 64 (
    curl -L -k -o "%PYTHON_INSTALLER%" "%PYTHON_URL%" || (
        call :handle_error "Failed to download Python installer" "Python Download"
    )
) else (
    curl -L -k -o "%PYTHON_INSTALLER%" "%PYTHON_URL_32BIT%" || (
        call :handle_error "Failed to download Python installer" "Python Download"
    )
)

call :display "Installing Python (please wait)..."
start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=0 || (
    call :handle_error "Python installation failed" "Python Install"
)

:python_ok
call :verify_python

:: Step 2: FFmpeg Installation
call :display "Step 2/8: Checking FFmpeg..."
where ffmpeg >nul 2>&1
if %errorlevel% equ 0 (
    call :display "FFmpeg is already installed :)"
    goto :ffmpeg_ok
)

call :display "Downloading FFmpeg (%ARCH%-bit)..."
if %ARCH% equ 64 (
    curl -L -k -o ffmpeg.zip "%FFMPEG_URL%" || (
        call :handle_error "Failed to download FFmpeg" "FFmpeg Download"
    )
) else (
    curl -L -k -o ffmpeg.zip "%FFMPEG_URL_32BIT%" || (
        call :handle_error "Failed to download FFmpeg" "FFmpeg Download"
    )
)

call :display "Extracting FFmpeg..."
powershell -command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.ffmpeg'" || (
    call :handle_error "Failed to extract FFmpeg" "FFmpeg Extract"
)

set "PATH=%~dp0.ffmpeg\bin;%PATH%"
:ffmpeg_ok

:: Steps 3-8: Python Environment Setup
call :display "Step 3/8: Creating virtual environment..."
if not exist "venv" (
    python -m venv venv || (
        call :handle_error "Failed to create virtual environment" "Venv Creation"
    )
)

call :display "Step 4/8: Activating virtual environment..."
call venv\Scripts\activate.bat || (
    call :handle_error "Failed to activate virtual environment" "Venv Activation"
)

call :display "Step 5/8: Updating pip..."
python -m pip install --upgrade pip || (
    call :handle_error "Failed to update pip" "Pip Update"
)

if exist requirements.txt (
    call :display "Step 6/8: Installing requirements..."
    pip install -r requirements.txt || (
        call :handle_error "Failed to install requirements" "Requirements Install"
    )
) else (
    call :display "No requirements.txt found, skipping..."
)

call :display "Step 7/8: Installing PyTorch %TORCH_VERSION%..."
pip install torch==%TORCH_VERSION% --index-url https://download.pytorch.org/whl/cpu || (
    call :handle_error "Failed to install PyTorch" "PyTorch Install"
)

call :display "Step 8/8: Installing llama-cpp-python %LLAMA_CPP_VERSION%..."
pip install llama-cpp-python==%LLAMA_CPP_VERSION% || (
    call :handle_error "Failed to install llama-cpp-python" "Llama Install"
)

:: ==================================================
:: Finalization
:: ==================================================
del python_installer.exe 2>nul
del ffmpeg.zip 2>nul

echo.
echo ===========================================
echo  All Done! Emily's Transcriptor is running
echo ===========================================
echo.
echo ------------------------------------------------
echo.
echo  (Press any key to close this window)
pause >nul

:: Launch application
python -c "from main import main; main()" || (
    call :handle_error "Failed to launch application" "App Launch"
)

endlocal
exit /b 0