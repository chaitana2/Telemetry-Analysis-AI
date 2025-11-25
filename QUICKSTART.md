# Telemetry Analysis Tool - Quick Start Guide

This guide will get you up and running with the Telemetry Analysis Tool in under 5 minutes.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning)
- pip (Python package installer)

**Platform-Specific Guides**:
- [Arch Linux Installation](docs/INSTALL_ARCH.md) - For Arch, Manjaro, EndeavourOS users

## Quick Install (Automated)

We provide automated installation scripts:

**Debian/Ubuntu:**
```bash
./install-debian.sh
```

**Arch Linux:**
```bash
./install-arch.sh
```

**macOS:**
```bash
./install-macos.sh
```

**Windows:**
```cmd
install-windows.bat
```

## Manual Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/chaitana2/Telemetry-Analysis-AI.git
cd Telemetry-Analysis-AI
```

### Step 2: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Installation time**: ~2-5 minutes

### Step 4: Verify Installation

## Quick Test

```bash
# Run tests to verify installation
pytest tests/

# Launch the application
python src/main.py
```

## Import Your First Dataset

1. Click **"Import CSV"** button
2. Select a Toyota-format telemetry CSV file
3. View the processed data in the Data View tab

## Example CSV Format

```csv
POSITION,NUMBER,DRIVER,TEAM,VEHICLE,LAPS,TOTAL_TIME,GAP_FIRST,FL_TIME,FL_KPH,STATUS
1,14,Driver Name,Team Name,Car Model,50,1:30:45.123,,1:35.678,160.5,Running
```

## Next Steps

- Read the full [README.md](README.md) for detailed features
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Browse API docs: `mkdocs serve` then visit http://localhost:8000

## Troubleshooting

**Import Error**: Ensure your CSV has the required columns (POSITION, NUMBER, TOTAL_TIME, etc.)

**UI Not Launching**: 
- Check that PyQt6 is installed: `pip show PyQt6`
- On Linux, install: `sudo apt install libxcb-xinerama0`

**Tests Failing**: 
- Verify Python version is 3.8+: `python --version`
- Ensure you're in the virtual environment (look for `(venv)` in prompt)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

**Virtual Environment Issues**:
- Windows PowerShell: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Make sure you activated the venv before installing packages

**Performance Issues**:
- Ensure you have at least 4GB RAM available
- Close other applications when processing large datasets

## Support

- GitHub Issues: [Report a bug](https://github.com/chaitana2/Telemetry-Analysis-AI/issues/new/choose)
- Documentation: [Full docs](https://github.com/chaitana2/Telemetry-Analysis-AI/tree/main/docs)
