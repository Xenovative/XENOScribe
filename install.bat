@echo off
echo ========================================
echo XENOscribe Installation Script
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version

:: Create virtual environment
echo.
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install PyTorch first (for better compatibility)
echo.
echo Installing PyTorch...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

:: Install other requirements
echo.
echo Installing application dependencies...
pip install -r requirements.txt

:: Check if FFmpeg is available
echo.
echo Checking for FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: FFmpeg not found in PATH
    echo FFmpeg is required for audio/video processing
    echo.
    echo Please install FFmpeg:
    echo 1. Download from: https://ffmpeg.org/download.html
    echo 2. Extract to a folder
    echo 3. Add the bin folder to your PATH environment variable
    echo.
    echo Or use chocolatey: choco install ffmpeg
    echo Or use winget: winget install ffmpeg
    echo.
) else (
    echo FFmpeg found and ready!
)

:: Download Whisper model
echo.
echo Downloading Whisper base model (this may take a few minutes)...
python -c "import whisper; whisper.load_model('base')"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run XENOscribe:
echo 1. Double-click 'run.bat'
echo 2. Or run: python app.py
echo.
echo The app will be available at: http://localhost:5000
echo.
pause
