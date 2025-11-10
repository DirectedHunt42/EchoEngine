#!/bin/bash
# Set -e ensures the script exits immediately if any command fails
set -e

# --- Configuration ---

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# Build Toggles
COMPILE_ECHO_HUB="YES"
COMPILE_ASCII="NO"
COMPILE_EDITOR="NO"

# Main Directories
OUTPUT_DIR="$SCRIPT_DIR/dist"
LOG_DIR="$SCRIPT_DIR/Log"
TEMP_ICON_DIR="$LOG_DIR/TempImages"

# --- Define Icon Paths ---
ECHO_HUB_ICON_ICO="$SCRIPT_DIR/Engine_editor/Icons/Echo_hub.ico"
ASCII_ICON_ICO="$SCRIPT_DIR/Engine_editor/Icons/App_icon/Ascii.ico"
EDITOR_ICON_ICO="$SCRIPT_DIR/Engine_editor/Icons/App_icon/Echo_editor.ico"

ECHO_HUB_ICON_PNG="$TEMP_ICON_DIR/Echo_hub.png"
ASCII_ICON_PNG="$TEMP_ICON_DIR/Ascii.png"
EDITOR_ICON_PNG="$TEMP_ICON_DIR/Echo_editor.png"

# --- PyInstaller Data Definitions (Source Path:Destination Path) ---
# Using the COLON (:) separator for Linux/macOS and simple destinations.
DATA_1="$SCRIPT_DIR/Engine_editor/Icons/Echo_hub.ico:Icons"
DATA_2="$SCRIPT_DIR/Engine_editor/Icons/App_icon/Ascii.ico:Icons/App_icon"

EDITOR_DATA_1="$SCRIPT_DIR/Engine_editor/Icons:Icons"
EDITOR_DATA_2="$SCRIPT_DIR/Engine_editor/Docs:Docs"
EDITOR_DATA_3="$SCRIPT_DIR/Engine_editor/Fonts:Fonts"
EDITOR_DATA_4=""

# --- Script Files ---
ECHO_HUB_SCRIPT="Echo_hub.py"
ECHO_HUB_BUILD_NAME="Echo_hub"

ASCII_SCRIPT="Ascii_generator.py"
ASCII_BUILD_NAME="Ascii_generator"

EDITOR_SCRIPT="Engine_editor/Echo_editor.py"
EDITOR_BUILD_NAME="Echo_editor"

# --- Hidden Imports (CRITICAL for CustomTkinter/Pillow) ---
# Explicitly including modules that PyInstaller often misses when linking PIL/tkinter
# and core parts of customtkinter to prevent runtime ModuleNotFoundError.
# Based on the import lists provided.
HIDDEN_IMPORTS=(
    "PIL._tkinter_finder"
    "PIL._imagingtk"
    "customtkinter"
    "customtkinter.windows"
    "customtkinter.windows.widgets"
    "customtkinter.windows.widgets.image"
    "tkinter.font" # Added as tkinter.font was imported as tkFont
)

# Build the hidden imports arguments string
HIDDEN_IMPORT_ARGS=""
for module in "${HIDDEN_IMPORTS[@]}"; do
    HIDDEN_IMPORT_ARGS="$HIDDEN_IMPORT_ARGS --hidden-import=$module"
done


# ===================================================================
# ==================== UTILITY FUNCTIONS ============================
# ===================================================================

# Check for PyInstaller
check_pyinstaller() {
    if ! command -v pyinstaller &> /dev/null; then
        echo "PyInstaller not found. Installing..."
        pip install pyinstaller
    fi
}

# Check for ImageMagick and install if needed
check_imagemagick() {
    if ! command -v convert &> /dev/null; then
        echo "--------------------------------------------------------"
        echo "❌ ImageMagick ('convert' command) not found."
        echo "You must install ImageMagick to convert the icons to PNG."
        echo "Try: 'sudo apt install imagemagick' (Linux) or 'brew install imagemagick' (macOS)"
        echo "--------------------------------------------------------"
        exit 1
    fi
}

# Convert the largest icon from ICO to PNG
convert_icon_to_png() {
    local ico_path=$1
    local png_path=$2
    # The [0] selects the largest icon/image inside the ICO file
    convert "$ico_path[0]" "$png_path"
    echo "Converted $ico_path to $png_path"
}

# ===================================================================
# ======================== SETUP AND CLEANUP ==========================
# ===================================================================

echo "Checking dependencies..."
check_pyinstaller
check_imagemagick

echo "Setting up directories..."
mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$TEMP_ICON_DIR"

echo "Cleaning old build artifacts from $LOG_DIR..."
rm -rf "$LOG_DIR/build"
rm -f "$LOG_DIR"/*.spec
rm -f "$LOG_DIR"/*.log
rm -f "$LOG_DIR"/*.sln

# ===================================================================
# ======================= ICON CONVERSION ===========================
# ===================================================================

echo "Converting ICO icons to PNG in $TEMP_ICON_DIR..."
convert_icon_to_png "$ECHO_HUB_ICON_ICO" "$ECHO_HUB_ICON_PNG"
convert_icon_to_png "$ASCII_ICON_ICO" "$ASCII_ICON_PNG"
convert_icon_to_png "$EDITOR_ICON_ICO" "$EDITOR_ICON_PNG"

# ===================================================================
# ========================= BUILD PROCESS ===========================
# ===================================================================

# --- 1. Compile Echo Hub ---
if [ "$COMPILE_ECHO_HUB" = "YES" ]; then
    echo
    echo "---------------------------------"
    echo "Compiling $ECHO_HUB_SCRIPT..."
    echo "---------------------------------"
    
    # Use the temporary PNG icon for the build and inject hidden imports
    pyinstaller --noconfirm --onefile --windowed \
        --icon "$ECHO_HUB_ICON_PNG" \
        --clean \
        $HIDDEN_IMPORT_ARGS \
        --add-data="$DATA_1" \
        --add-data="$DATA_2" \
        --distpath "$OUTPUT_DIR" \
        --workpath "$LOG_DIR/build/$ECHO_HUB_BUILD_NAME" \
        --specpath "$LOG_DIR" \
        "$SCRIPT_DIR/$ECHO_HUB_SCRIPT"

    if [ $? -ne 0 ]; then
        echo -e "\n\n\342\226\210\342\226\210\342\226\210 ERROR: Failed to compile $ECHO_HUB_SCRIPT$. See output above. \342\226\210\342\226\210\342\226\210"
        exit 1
    fi
    echo "Successfully compiled $ECHO_HUB_SCRIPT -> $OUTPUT_DIR"
else
    echo
    echo "--- Skipping Echo Hub (toggle not set to YES) ---"
fi

# --- 2. Compile Ascii Generator ---
if [ "$COMPILE_ASCII" = "YES" ]; then
    echo
    echo "---------------------------------"
    echo "Compiling $ASCII_SCRIPT..."
    echo "---------------------------------"

    # Use the temporary PNG icon for the build and inject hidden imports
    pyinstaller --noconfirm --onefile --windowed \
        --icon "$ASCII_ICON_PNG" \
        --clean \
        $HIDDEN_IMPORT_ARGS \
        --add-data="$DATA_1" \
        --add-data="$DATA_2" \
        --distpath "$OUTPUT_DIR" \
        --workpath "$LOG_DIR/build/$ASCII_BUILD_NAME" \
        --specpath "$LOG_DIR" \
        "$SCRIPT_DIR/$ASCII_SCRIPT"

    if [ $? -ne 0 ]; then
        echo -e "\n\n\342\226\210\342\226\210\342\226\210 ERROR: Failed to compile $ASCII_SCRIPT$. See output above. \342\226\210\342\226\210\342\226\210"
        exit 1
    fi
    echo "Successfully compiled $ASCII_SCRIPT -> $OUTPUT_DIR"
else
    echo
    echo "--- Skipping Ascii Generator (toggle not set to YES) ---"
fi

# --- 3. Compile Echo Editor ---
if [ "$COMPILE_EDITOR" = "YES" ]; then
    echo
    echo "---------------------------------"
    echo "Compiling $EDITOR_SCRIPT..."
    echo "---------------------------------"

    # Build a string of extra arguments for the editor, using --add-data="$VARIABLE" syntax
    EDITOR_EXTRA_ARGS=""
    if [ -n "$EDITOR_DATA_1" ]; then EDITOR_EXTRA_ARGS="$EDITOR_EXTRA_ARGS --add-data=\"$EDITOR_DATA_1\""; fi
    if [ -n "$EDITOR_DATA_2" ]; then EDITOR_EXTRA_ARGS="$EDITOR_EXTRA_ARGS --add-data=\"$EDITOR_DATA_2\""; fi
    if [ -n "$EDITOR_DATA_3" ]; then EDITOR_EXTRA_ARGS="$EDITOR_EXTRA_ARGS --add-data=\"$EDITOR_DATA_3\""; fi
    if [ -n "$EDITOR_DATA_4" ]; then EDITOR_EXTRA_ARGS="$EDITOR_EXTRA_ARGS --add-data=\"$EDITOR_DATA_4\""; fi

    # Use the temporary PNG icon for the build and inject hidden imports
    # We use 'eval' here to correctly parse the dynamically built EDITOR_EXTRA_ARGS string
    eval pyinstaller --noconfirm --onefile --windowed \
        --icon \""$EDITOR_ICON_PNG"\" \
        --clean \
        $HIDDEN_IMPORT_ARGS \
        --add-data=\"$DATA_1\" \
        --add-data=\"$DATA_2\" \
        "$EDITOR_EXTRA_ARGS" \
        --distpath \""$OUTPUT_DIR"\" \
        --workpath \""$LOG_DIR/build/$EDITOR_BUILD_NAME"\" \
        --specpath \""$LOG_DIR"\" \
        \""$SCRIPT_DIR/$EDITOR_SCRIPT"\"

    if [ $? -ne 0 ]; then
        echo -e "\n\n\342\226\210\342\226\210\342\226\210 ERROR: Failed to compile $EDITOR_SCRIPT$. See output above. \342\226\210\342\226\210\342\226\210"
        exit 1
    fi
    echo "Successfully compiled $EDITOR_SCRIPT -> $OUTPUT_DIR"
else
    echo
    echo "--- Skipping Echo Editor (toggle not set to YES) ---"
fi

# ===================================================================
# ========================== FINAL CLEANUP ==========================
# ===================================================================

echo
echo "Cleaning up temporary icon files..."
rm -rf "$TEMP_ICON_DIR"

echo
echo "==============================="
echo "\342\235\223 Build process finished!"
echo
echo "Build Toggles:"
echo "  - Echo Hub:   [$COMPILE_ECHO_HUB]"
echo "  - Ascii Gen:  [$COMPILE_ASCII]"
echo "  - Echo Editor: [$COMPILE_EDITOR]"
echo
echo "Executables: $OUTPUT_DIR"
echo "Logs and temporary build files: $LOG_DIR"
echo "==============================="