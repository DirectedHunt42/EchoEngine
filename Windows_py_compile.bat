@echo off
setlocal enabledelayedexpansion

REM Get the directory of this script
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM ===================================================================
REM ==================== CONFIGURATION SECTION ========================
REM ===================================================================
REM   Define all your scripts, icons, and paths here.

REM  Build Toggles 
REM   Set to "YES" to compile, any other value to skip
set "COMPILE_ECHO_HUB=YES"
set "COMPILE_ASCII=YES"
set "COMPILE_EDITOR=YES"

REM  Main Directories 
set "OUTPUT_DIR=%SCRIPT_DIR%\dist"
set "LOG_DIR=%SCRIPT_DIR%\Log"

REM  Script 1: Echo Hub 
set "ECHO_HUB_SCRIPT=Echo_hub.py"
set "ECHO_HUB_ICON=%SCRIPT_DIR%\Engine_editor\Icons\Echo_hub.ico"
set "ECHO_HUB_BUILD_NAME=Echo_hub"

REM  Script 2: Ascii Generator 
set "ASCII_SCRIPT=Ascii_generator.py"
set "ASCII_ICON=%SCRIPT_DIR%\Engine_editor\Icons\App_icon\Ascii.ico"
set "ASCII_BUILD_NAME=Ascii_generator"

REM  Script 3: Echo Editor 
set "EDITOR_SCRIPT=Engine_editor\Echo_editor.py"
set "EDITOR_ICON=%SCRIPT_DIR%\Engine_editor\Icons\App_icon\Echo_editor.ico"
set "EDITOR_BUILD_NAME=Echo_editor"

    REM  Echo Editor: Extra Data Folders/Files 
    REM   (These are ADDED to the shared data files for the Editor ONLY)
    REM   Format: "SOURCE_PATH;DESTINATION_IN_EXE"
    REM *** FIX: Using simple destination folders (e.g., Icons) ***
    set "EDITOR_DATA_1=%SCRIPT_DIR%\Engine_editor\Icons;Icons"
    set "EDITOR_DATA_2=%SCRIPT_DIR%\Engine_editor\Docs;Docs"
    set "EDITOR_DATA_3=%SCRIPT_DIR%\Engine_editor\Fonts;Fonts"
    set "EDITOR_DATA_4="

REM  Shared Data Files 
REM   These will be added to ALL compiled executables.
REM *** FIX: Using simple destination folders (e.g., Icons) ***
set "DATA_1=%SCRIPT_DIR%\Engine_editor\Icons\Echo_hub.ico;Icons"
set "DATA_2=%SCRIPT_DIR%\Engine_editor\Icons\App_icon\Ascii.ico;Icons\App_icon"

REM ===================================================================
REM ================== SCRIPT EXECUTION (No Need to Edit) =============
REM ===================================================================

REM  1. Dependency Checks 
echo Checking dependencies...
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM  2. Setup Directories 
echo Setting up directories...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM  3. Clean Old Build Artifacts 
echo Cleaning old build artifacts from %LOG_DIR%...
if exist "%LOG_DIR%\build" rmdir /s /q "%LOG_DIR%\build"
del /q "%LOG_DIR%\*.spec" 2>nul
del /q "%LOG_DIR%\*.log" 2>nul
del /q "%LOG_DIR%\*.sln" 2>nul

REM ===================================================================
REM ========================= BUILD PROCESS ===========================
REM ===================================================================

REM  1. Compile Echo Hub 
if /I "%COMPILE_ECHO_HUB%" == "YES" (
    echo.
    echo 
    echo Compiling %ECHO_HUB_SCRIPT%...
    echo 
    pyinstaller --noconfirm --onefile --windowed ^
        --icon "%ECHO_HUB_ICON%" ^
        --clean ^
        --add-data "%DATA_1%" ^
        --add-data "%DATA_2%" ^
        --distpath "%OUTPUT_DIR%" ^
        --workpath "%LOG_DIR%\build\%ECHO_HUB_BUILD_NAME%" ^
        --specpath "%LOG_DIR%" ^
        "%SCRIPT_DIR%\%ECHO_HUB_SCRIPT%"

    REM Check for failure
    if %errorlevel% neq 0 (
        echo.
        echo ▩▩▩ ERROR: Failed to compile %ECHO_HUB_SCRIPT%. See output above. ▩▩▩
        pause
        goto :eof
    )
    echo Successfully compiled %ECHO_HUB_SCRIPT% -> %OUTPUT_DIR%
) else (
    echo.
    echo  Skipping Echo Hub (toggle not set to YES) 
)

REM  2. Compile Ascii Generator 
if /I "%COMPILE_ASCII%" == "YES" (
    echo.
    echo 
    echo Compiling %ASCII_SCRIPT%...
    echo 
    pyinstaller --noconfirm --onefile --windowed ^
        --icon "%ASCII_ICON%" ^
        --clean ^
        --add-data "%DATA_1%" ^
        --add-data "%DATA_2%" ^
        --distpath "%OUTPUT_DIR%" ^
        --workpath "%LOG_DIR%\build\%ASCII_BUILD_NAME%" ^
        --specpath "%LOG_DIR%" ^
        "%SCRIPT_DIR%\%ASCII_SCRIPT%"

    REM Check for failure
    if %errorlevel% neq 0 (
        echo.
        echo ▩▩▩ ERROR: Failed to compile %ASCII_SCRIPT%. See output above. ▩▩▩
        pause
        goto :eof
    )
    echo Successfully compiled %ASCII_SCRIPT% -> %OUTPUT_DIR%
) else (
    echo.
    echo  Skipping Ascii Generator (toggle not set to YES) 
)

REM  3. Compile Echo Editor 
if /I "%COMPILE_EDITOR%" == "YES" (
    echo.
    echo 
    echo Compiling %EDITOR_SCRIPT%...
    echo 

    REM *** Build a string of extra arguments for the editor ***
    set "EDITOR_EXTRA_ARGS="
    if not "%EDITOR_DATA_1%" == "" ( set "EDITOR_EXTRA_ARGS=!EDITOR_EXTRA_ARGS! --add-data "%EDITOR_DATA_1%"" )
    if not "%EDITOR_DATA_2%" == "" ( set "EDITOR_EXTRA_ARGS=!EDITOR_EXTRA_ARGS! --add-data "%EDITOR_DATA_2%"" )
    if not "%EDITOR_DATA_3%" == "" ( set "EDITOR_EXTRA_ARGS=!EDITOR_EXTRA_ARGS! --add-data "%EDITOR_DATA_3%"" )
    if not "%EDITOR_DATA_4%" == "" ( set "EDITOR_EXTRA_ARGS=!EDITOR_EXTRA_ARGS! --add-data "%EDITOR_DATA_4%"" )

    pyinstaller --noconfirm --onefile --windowed ^
        --icon "%EDITOR_ICON%" ^
        --clean ^
        --add-data "%DATA_1%" ^
        --add-data "%DATA_2%" ^
        !EDITOR_EXTRA_ARGS! ^
        --distpath "%OUTPUT_DIR%" ^
        --workpath "%LOG_DIR%\build\%EDITOR_BUILD_NAME%" ^
        --specpath "%LOG_DIR%" ^
        "%SCRIPT_DIR%\%EDITOR_SCRIPT%"

    REM Check for failure
    if %errorlevel% neq 0 (
        echo.
        echo ▩▩▩ ERROR: Failed to compile %EDITOR_SCRIPT%. See output above. ▩▩▩
        pause
        goto :eof
    )
    echo Successfully compiled %EDITOR_SCRIPT% -> %OUTPUT_DIR%
) else (
    echo.
    echo  Skipping Echo Editor (toggle not set to YES) 
)

REM  Final 
echo.
echo ===============================
echo ✓ Build process finished!
echo.
echo Build Toggles:
echo   - Echo Hub:   [%COMPILE_ECHO_HUB%]
echo   - Ascii Gen:  [%COMPILE_ASCII%]
echo   - Echo Editor: [%COMPILE_EDITOR%]
echo.
echo Executables: %OUTPUT_DIR%
echo Logs and temporary build files: %LOG_DIR%
echo ===============================
pause
goto :eof