@echo off
echo ========================================
echo XENOscribe Quick Setup
echo ========================================
echo.
echo This will install XENOscribe and run it immediately.
echo.
pause

:: Run installation
call install.bat

:: Check if installation was successful
if %errorlevel% neq 0 (
    echo.
    echo Installation failed. Please check the errors above.
    pause
    exit /b 1
)

:: Create desktop shortcut
echo.
echo Creating desktop shortcut...
if exist "assets\favicon.ico" (
    cscript //nologo create_shortcut.vbs
    if %errorlevel% equ 0 (
        echo Desktop shortcut "XENOscribe" created successfully!
    ) else (
        echo Warning: Could not create desktop shortcut
    )
) else if exist "assets\xeno.png" (
    cscript //nologo create_shortcut.vbs
    if %errorlevel% equ 0 (
        echo Desktop shortcut "XENOscribe" created successfully!
    ) else (
        echo Warning: Could not create desktop shortcut
    )
) else (
    echo Warning: Icon files not found, creating shortcut without icon...
    cscript //nologo create_shortcut.vbs
)

:: Ask user if they want to run the app now
echo.
set /p choice="Would you like to start XENOscribe now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo Starting XENOscribe...
    call run.bat
) else (
    echo.
    echo Setup complete! 
    echo - Use the desktop shortcut "XENOscribe" to run the app
    echo - Or run 'run.bat' from this folder
    pause
)
