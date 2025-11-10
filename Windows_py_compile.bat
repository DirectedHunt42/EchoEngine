@echo off
setlocal enabledelayedexpansion

REM Get the directory of this script
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Output directories
set "OUTPUT_DIR=%SCRIPT_DIR%\dist"
set "LOG_DIR=%SCRIPT_DIR%\Log"

REM List of Python scripts
set SCRIPTS=Echo_hub.py Ascii_generator.py Echo_editor.py

REM Icon paths (Windows can still use .ico)
set "ECHO_HUB_ICON=%SCRIPT_DIR%\Engine_editor\Icons\Echo_hub.ico"
set "ASCII_ICON=%SCRIPT_DIR%\Engine_editor\Icons\App_icon\Ascii.ico"

REM Ensure PyInstaller is installed
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Create directories if they don't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Clean old logs
if exist "%LOG_DIR%\build" rmdir /s /q "%LOG_DIR%\build"
del /q "%LOG_DIR%\*.spec" 2>nul
del /q "%LOG_DIR%\*.log" 2>nul
del /q "%LOG_DIR%\*.sln" 2>nul

REM Compile scripts
for %%F in (%SCRIPTS%) do (
    echo.
    echo Compiling %%F...
    pyinstaller --noconfirm --onefile --windowed ^
        --icon "%ECHO_HUB_ICON%" ^
        --clean ^
        --add-data "%ECHO_HUB_ICON%;Engine_editor\Icons" ^
        --add-data "%ASCII_ICON%;Engine_editor\App_icon" ^
        --distpath "%OUTPUT_DIR%" ^
        "%SCRIPT_DIR%\%%F"
    echo Compiled %%F → %OUTPUT_DIR%
)

REM Move build artifacts
echo.
echo Organizing build artifacts...

if exist "%SCRIPT_DIR%\build" (
    if exist "%LOG_DIR%\build" rmdir /s /q "%LOG_DIR%\build"
    move "%SCRIPT_DIR%\build" "%LOG_DIR%" >nul
)

for %%F in ("%SCRIPT_DIR%\*.spec") do move "%%F" "%LOG_DIR%" >nul 2>&1
for %%F in ("%SCRIPT_DIR%\*.log") do move "%%F" "%LOG_DIR%" >nul 2>&1
for %%F in ("%SCRIPT_DIR%\*.sln") do move "%%F" "%LOG_DIR%" >nul 2>&1

echo.
echo Compilation complete!
echo Executables: %OUTPUT_DIR%
echo Logs, .sln and temporary build files: %LOG_DIR%
pause