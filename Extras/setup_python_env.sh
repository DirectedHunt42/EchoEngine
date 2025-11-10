#!/usr/bin/env bash
set -e

# ============================================
# Fully Automated Python Environment Setup + Validation (WSL)
# ============================================

PYTHON_CMD="python3"
PIP_CMD="pip3"

# --- Python imports to verify ---
PYTHON_IMPORTS=(
"os"
"sys"
"shutil"
"webbrowser"
"zipfile"
"threading"
"subprocess"
"customtkinter"
"tkinter"
"PIL"
"urllib.request"
"json"
"platform"
"CTkMessagebox"
"traceback"
"collections"
"pygame"
)

# --- Pip packages to install ---
PIP_PACKAGES=("customtkinter" "CTkMessagebox" "Pillow" "pygame")

echo "🚀 Starting automated Python environment setup and validation..."
export DEBIAN_FRONTEND=noninteractive

# --- Update package list ---
echo "🔄 Updating apt repositories..."
sudo apt-get update -qq

# --- Install system dependencies ---
echo "📦 Installing system dependencies..."
sudo apt-get install -y -qq python3 python3-pip python3-tk tk-dev libjpeg-dev zlib1g-dev

# --- Verify Python installation ---
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python installation failed. Please check your system."
    exit 1
fi
echo "✅ Python 3 detected: $($PYTHON_CMD --version)"

# --- Verify pip installation ---
if ! command -v $PIP_CMD &> /dev/null; then
    echo "❌ pip installation failed. Please check your system."
    exit 1
fi
echo "✅ pip detected: $($PIP_CMD --version)"

# --- Install required pip packages ---
echo "📦 Installing/updating required Python packages..."
for pkg in "${PIP_PACKAGES[@]}"; do
    echo "  → Installing $pkg..."
    $PIP_CMD install -q -U --break-system-packages "$pkg"
done

# --- Validate imports ---
echo
echo "🔍 Validating Python imports..."
FAILED_IMPORTS=()
for module in "${PYTHON_IMPORTS[@]}"; do
    if $PYTHON_CMD -c "import $module" >/dev/null 2>&1; then
        echo "✅ Import OK: $module"
    else
        echo "❌ Failed import: $module"
        FAILED_IMPORTS+=("$module")
    fi
done

# --- Results ---
echo
if [ ${#FAILED_IMPORTS[@]} -eq 0 ]; then
    echo "🎉 All Python modules validated successfully!"
else
    echo "⚠️ Some imports failed:"
    for m in "${FAILED_IMPORTS[@]}"; do
        echo "   - $m"
    done
    echo "You may need to reinstall or troubleshoot those manually."
fi

echo
echo "✅ Setup and validation complete (no user input required)."