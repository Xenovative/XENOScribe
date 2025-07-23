@echo off
echo ========================================
echo Starting XENOscribe by Xenovative
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run 'install.bat' first to set up the application.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if app.py exists
if not exist "app.py" (
    echo ERROR: app.py not found!
    echo Make sure you're running this from the correct directory.
    echo.
    pause
    exit /b 1
)

:: Start the application and open browser
echo.
echo Loading Whisper model and starting server...
echo This may take a moment on first run...
echo.
echo XENOscribe will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
start http://localhost:5000

python app.py

echo.
echo XENOscribe has stopped.
pause
