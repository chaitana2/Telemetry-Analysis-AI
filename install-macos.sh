#!/bin/bash
# Automated installation script for macOS
# Telemetry Analysis Tool

set -e  # Exit on error

echo "=========================================="
echo "Telemetry Analysis Tool - Installer"
echo "For macOS"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Check if Homebrew is installed
echo "Checking Homebrew installation..."
if command -v brew &> /dev/null; then
    print_status "Homebrew found"
else
    print_warning "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    print_status "Homebrew installed"
fi

# Check Python version
echo ""
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
else
    print_warning "Python 3 not found. Installing..."
    brew install python3
    print_status "Python 3 installed"
fi

# Check Python version is 3.8+
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    print_warning "Upgrading Python..."
    brew upgrade python3
fi

# Install system dependencies
echo ""
echo "Installing system dependencies..."
brew install qt6 || print_warning "Qt6 already installed or not needed"
print_status "System dependencies checked"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
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
echo "For more information, see README.md"
echo ""
