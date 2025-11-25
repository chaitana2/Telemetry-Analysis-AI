# Telemetry Analysis Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A cross-platform telemetry analysis tool for race data, optimized for Toyota's CSV format. This tool leverages AI to provide insights into driver performance, predictive lap timing, and anomaly detection.

## Features

- **Data Ingestion**: Robust parsing of Toyota-format CSV telemetry files.
- **Data Preprocessing**: Automatic cleaning and conversion of time formats (e.g., `MM:SS.sss`, `+SS.sss`).
- **AI Analysis**:
    - **Driver Performance Trends**: Analyze consistency and pace.
    - **Predictive Lap Timing**: LSTM-based neural network for forecasting lap times.
    - **Anomaly Detection**: Isolation Forest model to identify outliers in vehicle performance.
- **Visualization**: Interactive dashboard built with PyQt6 and Matplotlib.
- **Cross-Platform**: Compatible with Linux, Windows, and macOS.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/chaitana2/Telemetry-Analysis-AI.git
   cd Telemetry-Analysis-AI
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To launch the application:

```bash
python src/main.py
```

### Importing Data
1. Click the "Import CSV" button in the top bar.
2. Select a valid Toyota telemetry CSV file.
3. The data will be loaded into the "Data View" tab.

## Development

### Running Tests
Run the full test suite with coverage:
```bash
pytest --cov=src tests/
```

### Linting
Check code style compliance:
```bash
flake8 src/ tests/
```

### Documentation
Generate and serve documentation locally:
```bash
mkdocs serve
```

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
