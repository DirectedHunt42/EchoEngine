#!/bin/bash

# Get the absolute path of the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Output directories
OUTPUT_DIR="$SCRIPT_DIR/dist"
LOG_DIR="$SCRIPT_DIR/Log"

# --- Python Scripts & Icons ---
# (Using a more structured way to associate scripts with icons)
ECHO_HUB_SCRIPT="Echo_hub.py"
ASCII_SCRIPT="Ascii_generator.py"
EDITOR_SCRIPT="Echo_editor.py"

ECHO_HUB_ICON="$SCRIPT_DIR/Engine_editor/Icons/Echo_hub.png"
ASCII_ICON="$SCRIPT_DIR/Engine_editor/Icons/App_icon/Ascii.png"
# Assuming Editor uses the main icon, change if needed
EDITOR_ICON="$ECHO_HUB_ICON"

# --- Dependency Checks ---
echo "Checking dependencies..."

# Ensure PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Ensure Tkinter and Pillow dependencies (running as-needed)
# Note: 'sudo apt' will require your password
echo "Ensuring system dependencies (may ask for password)..."
sudo apt install -y python3-tk tk-dev libjpeg-dev zlib1g-dev
echo "Ensuring Python dependencies..."
pip install --upgrade pillow customtkinter

# --- Setup Directories ---
mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"

# Clean old logs and build artifacts
echo "Cleaning old build artifacts from $LOG_DIR..."
rm -rf "$LOG_DIR/build" "$LOG_DIR"/*.spec "$LOG_DIR"/*.log "$LOG_DIR"/*.sln 2>/dev/null

# --- Compile Functions ---
# This function handles the actual compilation and error checking
compile_script() {
  local script_name="$1"
  local icon_path="$2"
  local build_name="${script_name%.py}" # Removes .py extension

  echo
  echo "Compiling $script_name..."
  pyinstaller --noconfirm --onefile --windowed \
    --icon "$icon_path" \
    --clean \
    --add-data "$ECHO_HUB_ICON:Engine_editor/Icons" \
    --add-data "$ASCII_ICON:Engine_editor/Icons/App_icon" \
    --distpath "$OUTPUT_DIR" \
    --workpath "$LOG_DIR/build/$build_name" \
    --specpath "$LOG_DIR" \
    "$SCRIPT_DIR/$script_name" || { echo "🔥 ERROR: Failed to compile $script_name. See output above."; exit 1; }
    
  echo "Successfully compiled $script_name → $OUTPUT_DIR"
}

# --- Run Compilation ---
compile_script "$ECHO_HUB_SCRIPT" "$ECHO_HUB_ICON"
compile_script "$ASCII_SCRIPT" "$ASCII_ICON"
compile_script "$EDITOR_SCRIPT" "$EDITOR_ICON"

# The old "Organizing build artifacts" section is no longer needed

echo
echo "✅ Compilation complete!"
echo "Executables: $OUTPUT_DIR"
echo "Logs and temporary build files: $LOG_DIR"