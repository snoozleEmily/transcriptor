# Ensure Chocolatey is installed
if (!(Test-Path "$env:ProgramData\chocolatey")) {
    Write-Output "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    RefreshEnv
}

# Update Chocolatey and refresh sources
Write-Output "Updating Chocolatey..."
choco upgrade chocolatey -y
choco source update -n="chocolatey"

# Ensure FFmpeg is installed system-wide
if (!(Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Output "Installing FFmpeg..."
    choco install ffmpeg -y
} else {
    Write-Output "FFmpeg is already installed."
}

# Activate the correct Python virtual environment
$venvPath = "D:\Projects\Python-studies\transcriptor\env"
$venvActivate = "$venvPath\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Output "Activating virtual environment..."
    & $venvActivate
} else {
    Write-Output "Creating a new virtual environment..."
    python -m venv $venvPath
    & $venvActivate
}

# Upgrade pip
Write-Output "Upgrading pip..."
pip install --upgrade pip

# Install required Python packages
Write-Output "Installing required Python packages..."
pip install --upgrade ffmpeg-python openai-whisper fpdf

# Verify installation
Write-Output "Verifying package installation..."
$modules = @("ffmpeg", "whisper", "fpdf")
foreach ($module in $modules) {
    try {
        python -c "import $module; print('$module imported successfully')"
    } catch {
        Write-Output "Error importing $module. Reinstalling..."
        pip install --upgrade $module
    }
}

# Confirm correct Python interpreter
Write-Output "Confirming Python interpreter..."
python -c "import sys; print('Using Python:', sys.executable)"

Write-Output "Setup completed successfully!"
