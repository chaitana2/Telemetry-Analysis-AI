#!/bin/bash
# Automated installation script for Arch-based systems
# Telemetry Analysis Tool

set -e  # Exit on error

echo "=========================================="
echo "Telemetry Analysis Tool - Installer"
echo "For Arch/Manjaro/EndeavourOS"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Error: Please do not run this script as root or with sudo${NC}"
    exit 1
fi

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check Python version
echo "Checking Python installation..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
else
    print_warning "Python not found. Installing..."
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm python python-pip
    print_status "Python installed"
fi

# Check Python version is 3.8+
PYTHON_MAJOR=$(python -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo pacman -S --needed --noconfirm \
    python \
    python-pip \
    qt6-base \
    qt6-tools \
    libxcb \
    xcb-util-wm \
    xcb-util-image \
    xcb-util-keysyms \
    xcb-util-renderutil \
    git

print_status "System dependencies installed"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping..."
else
    python -m venv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
print_status "pip upgraded"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
echo "This may take 2-5 minutes..."
pip install -r requirements.txt --quiet
print_status "Python dependencies installed"

# Run tests
echo ""
echo "Running tests to verify installation..."
if pytest tests/ --quiet; then
    print_status "All tests passed!"
else
    print_error "Some tests failed. Please check the output above."
    exit 1
fi

# Success message
echo ""
echo "=========================================="
echo -e "${GREEN}Installation completed successfully!${NC}"
echo "=========================================="
echo ""
echo "To use the application:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python src/main.py"
echo ""
echo "  3. To deactivate the virtual environment:"
echo "     deactivate"
echo ""
echo "For more information, see README.md or docs/INSTALL_ARCH.md"
echo ""
