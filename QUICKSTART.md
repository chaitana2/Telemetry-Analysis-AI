# Telemetry Analysis Tool - Quick Start Guide

This guide will get you up and running with the Telemetry Analysis Tool in under 5 minutes.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning)

**Platform-Specific Guides**:
- [Arch Linux Installation](docs/INSTALL_ARCH.md) - For Arch, Manjaro, EndeavourOS users

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/telemetry-analysis-tool.git
cd telemetry-analysis-tool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

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

**UI Not Launching**: Check that PyQt6 is installed: `pip install PyQt6`

**Tests Failing**: Verify Python version is 3.8+: `python --version`

## Support

- GitHub Issues: [Report a bug](https://github.com/yourusername/telemetry-analysis-tool/issues)
- Documentation: [Full docs](https://yourusername.github.io/telemetry-analysis-tool/)
