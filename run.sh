#!/bin/bash
# Launch script for Linux (Debian/Ubuntu/Arch)
# Telemetry Analysis Tool

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Telemetry Analysis Tool - Launcher"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo "Please run the installation script first:"
    echo "  ./install-debian.sh  (for Debian/Ubuntu)"
    echo "  ./install-arch.sh    (for Arch Linux)"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}Virtual environment activated${NC}"
echo ""
echo "Launching Telemetry Analysis Tool..."
echo ""

# Launch the application
python src/main.py

# Deactivate when done
deactivate
