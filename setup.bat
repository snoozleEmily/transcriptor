:: OUTDATED -> Needs to be updated
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

:: Initial credits message
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

:: ---------------------------------------------------------------------
:: Function :display
:: Displays a message in a box
:: ---------------------------------------------------------------------
:display
echo.
echo ===========================================
echo  %~1
echo ===========================================
echo.
timeout /t 2 /nobreak >nul
goto :eof

:: ---------------------------------------------------------------------
:: MAIN SCRIPT
:: ---------------------------------------------------------------------
:main
call :display "Initializing Setup..."

:: ---------------------------------------------------------------------
:: Step 1: Check for Python (system or local)
:: ---------------------------------------------------------------------
call :display "Step 1/5: Checking Python..."
where python >nul 2>nul
if %errorlevel% equ 0 (
    call :display "Python is already installed :)"
    set "PYTHON_CMD=python"
) else (
    if exist ".python\python.exe" (
        call :display "Found local Python installation."
        set "PYTHON_CMD=%~dp0.python\python.exe"
        set "PATH=%~dp0.python;%PATH%"
    ) else (
        call :display "Python not found. Installing..."
        curl -L -o python.zip https://www.python.org/ftp/python/3.11.5/python-3.11.5-embed-amd64.zip
        mkdir .python
        tar -xf python.zip -C .python
        del python.zip

        :: Install pip for the local Python
        curl -L -o get-pip.py https://bootstrap.pypa.io/get-pip.py
        .python\python.exe get-pip.py
        del get-pip.py

        set "PYTHON_CMD=%~dp0.python\python.exe"
        set "PATH=%~dp0.python;%~dp0.python\Scripts;%PATH%"
    )
)

:: ---------------------------------------------------------------------
:: Step 2: Check for FFmpeg (system or local)
:: ---------------------------------------------------------------------
call :display "Step 2/5: Checking FFmpeg..."
where ffmpeg >nul 2>nul
if %errorlevel% equ 0 (
    call :display "FFmpeg is already installed :D"
) else (
    if exist ".ffmpeg\bin\ffmpeg.exe" (
        call :display "Found local FFmpeg installation."
        set "PATH=%~dp0.ffmpeg\bin;%PATH%"
    ) else (
        call :display "FFmpeg not found. Installing..."
        curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
        mkdir .ffmpeg
        tar -xf ffmpeg.zip -C .ffmpeg
        move .ffmpeg\ffmpeg-master-latest-win64-gpl\* .ffmpeg >nul
        rmdir /s /q .ffmpeg\ffmpeg-master-latest-win64-gpl
        del ffmpeg.zip
        set "PATH=%~dp0.ffmpeg\bin;%PATH%"
    )
)

:: ---------------------------------------------------------------------
:: Step 3: Set Up Virtual Environment
:: ---------------------------------------------------------------------
call :display "Step 3/5: Setting Up Environment..."
if not exist "venv" (
    %PYTHON_CMD% -m venv venv
)

:: Activate venv
call venv\Scripts\activate.bat

:: ---------------------------------------------------------------------
:: Step 4: Install Dependencies
:: ---------------------------------------------------------------------

:: ANTES de qualquer coisa, ativar o venv

:: TODO -> ajust the instaliation of torch
:: pip install torch==2.0.0 --index-url https://download.pytorch.org/whl/cpu


call :display "Step 4/5: Installing Dependencies..."
if exist requirements.txt (
    pip install -r requirements.txt >nul 2>&1
)

:: ---------------------------------------------------------------------
:: Step 5: Run main() from main.py
:: ---------------------------------------------------------------------
call :display "Step 5/5: Starting Emily's Transcriptor..."
python -c "from main import main; main()"

:: Final message
echo.
echo ===========================================
echo  All Done! Emily's Transcriptor is running
echo ===========================================
echo.
echo Although this is a hobby, creating these types of programs is quite challenging,
echo how about a star on my GitHub repository to support my work?
echo Come on... they're free :3
echo 
echo.
echo Embora isso seja um hobby, criar esse tipo de programa e bem desafiador, 
echo que tal uma estrelinha la no meu repositorio do GitHub para apoiar meu trabalho?
echo Fala serio... são de graca :3
echo.
echo ------------------------------------------------
echo.
echo  (Press any key to close this window)
pause >nul
endlocal