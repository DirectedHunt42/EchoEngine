#!/bin/bash

# Get the absolute path of the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Output directories
OUTPUT_DIR="$SCRIPT_DIR/dist"
LOG_DIR="$SCRIPT_DIR/Log"

# List of Python scripts to compile
SCRIPTS=(
  "Echo_hub.py"
  "Ascii_generator.py"
  "Echo_editor.py"
)

# Icon paths (PNG for Linux)
ECHO_HUB_ICON="$SCRIPT_DIR/Engine_editor/Icons/Echo_hub.png"
ASCII_ICON="$SCRIPT_DIR/Engine_editor/Icons/App_icon/Ascii.png"

# Ensure PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Ensure Tkinter and Pillow dependencies
sudo apt install -y python3-tk tk-dev libjpeg-dev zlib1g-dev
pip install --upgrade pillow customtkinter

# Create required directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"

# Clean old logs
rm -rf "$LOG_DIR/build" "$LOG_DIR"/*.spec "$LOG_DIR"/*.log "$LOG_DIR"/*.sln 2>/dev/null

# Compile scripts
for script in "${SCRIPTS[@]}"; do
  echo
  echo "Compiling $script..."
  pyinstaller --noconfirm --onefile --windowed \
    --icon "$ECHO_HUB_ICON" \
    --clean \
    --add-data "$ECHO_HUB_ICON:Engine_editor/Icons" \
    --add-data "$ASCII_ICON:Engine_editor/Icons/App_icon" \
    --distpath "$OUTPUT_DIR" \
    "$SCRIPT_DIR/$script"
  echo "Compiled $script → $OUTPUT_DIR"
done

echo
echo "Organizing build artifacts..."

# Move the build folder
if [ -d "$SCRIPT_DIR/build" ]; then
  rm -rf "$LOG_DIR/build"
  mv "$SCRIPT_DIR/build" "$LOG_DIR/"
fi

# Move .spec, .log, and .sln files
find "$SCRIPT_DIR" -maxdepth 1 -type f \( -name "*.spec" -o -name "*.log" -o -name "*.sln" \) -exec mv {} "$LOG_DIR/" \; 2>/dev/null

echo
echo "✅ Compilation complete!"
echo "Executables: $OUTPUT_DIR"
echo "Logs, .sln and temporary build files: $LOG_DIR"