# Telemetry Analysis Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A cross-platform desktop application for analyzing race telemetry data with AI-powered insights. Designed for motorsport engineers, data analysts, and racing enthusiasts who need to extract meaningful patterns from Toyota-format CSV telemetry files.

---

## Overview

### Project Goals

The Telemetry Analysis Tool provides:
- **Automated data processing** for race telemetry in Toyota's official CSV format
- **AI-driven insights** including driver performance analysis, lap time prediction, and anomaly detection
- **Interactive visualization** through a modern desktop interface
- **Cross-platform compatibility** for Linux, Windows, and macOS environments

### Scope

This tool is designed for **intermediate to advanced users** who understand motorsport telemetry concepts and want to leverage machine learning for deeper analysis. It handles session-level data including lap times, gaps, speeds, and vehicle status.

---

## Features

### 1. Data Ingestion & Preprocessing

**Toyota CSV Format Support**
- Parses official Toyota telemetry CSV files with fields: `POSITION`, `NUMBER`, `DRIVER`, `TEAM`, `VEHICLE`, `LAPS`, `TOTAL_TIME`, `GAP_FIRST`, `FL_TIME`, `FL_KPH`, `STATUS`
- Automatically handles missing or malformed data

**Time Format Conversion**
- Converts complex time strings to numeric seconds:
  - `1:30:45.123` (HH:MM:SS.sss) → 5445.123 seconds
  - `+1:14.985` (gap format) → 74.985 seconds
  - `+5.234` (simple gap) → 5.234 seconds
- Creates new columns with `_SEC` suffix for analysis

**Data Cleaning**
- Standardizes column names (uppercase, trimmed)
- Converts numeric fields with error handling
- Encodes categorical variables (e.g., STATUS, VEHICLE)

### 2. AI-Powered Analysis

#### Lap Time Predictor (LSTM Neural Network)
**Purpose**: Forecast future lap times based on historical patterns

**How It Works**:
- Uses Long Short-Term Memory (LSTM) architecture
- Input features: Lap number, position, gap to first, previous lap time
- Predicts next lap time with confidence intervals
- Useful for race strategy and pit stop planning

**Note**: Currently mocked due to environment constraints. Full PyTorch implementation available for production deployment.

#### Anomaly Detection (Isolation Forest)
**Purpose**: Identify unusual telemetry readings that may indicate mechanical issues or driver errors

**How It Works**:
- Scikit-learn's Isolation Forest algorithm
- Analyzes multi-dimensional telemetry data
- Flags outliers (e.g., sudden speed drops, erratic lap times)
- Configurable contamination threshold (default: 5%)

**Use Cases**:
- Detecting tire degradation
- Identifying mechanical failures
- Spotting driver mistakes

#### Race Coach (Performance Insights)
**Purpose**: Generate automated coaching feedback

**Metrics Analyzed**:
- **Consistency**: Standard deviation of lap times
- **Pace**: Average lap time vs. field
- **Trend Analysis**: Performance over session duration

**Example Output**:
```
Average Lap Time: 91.23s
Consistency (Std Dev): 0.42s
Driver is very consistent.
```

### 3. User Interface

**Main Window**
- Built with PyQt6 for native look and feel
- Responsive layout with tabbed interface
- File picker for CSV import

**Data View Tab**
- Displays loaded telemetry in sortable table
- Shows all original and computed columns
- Supports filtering and search (planned)

**Dashboard Tab**
- Visualization area for charts and graphs
- Lap time progression plots
- Gap analysis charts
- Speed distribution histograms

---

## Setup & Installation

### System Requirements

- **Operating System**: 
  - Linux: Ubuntu 20.04+, Fedora 35+, Arch Linux, Manjaro, EndeavourOS
  - Windows 10+
  - macOS 11+
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended for large datasets)
- **Disk Space**: 500MB for dependencies

### Prerequisites

Ensure you have Python and pip installed:
```bash
python3 --version  # Should be 3.8+
pip --version
```

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://https://github.com/chaitana2/Telemetry-Analysis-AI
   cd telemetry-analysis-tool
   ```

2. **Create Virtual Environment**
   ```bash
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   This installs:
   - `pandas` & `numpy` - Data processing
   - `scikit-learn` - Machine learning
   - `PyQt6` - User interface
   - `matplotlib` - Visualization
   - `pytest` & `pytest-cov` - Testing
   - `black` & `flake8` - Code quality
   - `mkdocs` & `mkdocstrings` - Documentation

4. **Verify Installation**
   ```bash
   pytest tests/
   ```
   All tests should pass.

---

## Usage Instructions

### Launching the Application

```bash
python src/main.py
```

The main window will open with two tabs: **Data View** and **Dashboard**.

### Importing Telemetry Files

1. Click the **"Import CSV"** button in the top toolbar
2. Navigate to your telemetry CSV file (Toyota format)
3. Select the file and click **Open**
4. Data will load and appear in the Data View tab

**Supported File Format Example**:
```csv
POSITION,NUMBER,DRIVER,TEAM,VEHICLE,LAPS,TOTAL_TIME,GAP_FIRST,FL_TIME,FL_KPH,STATUS
1,14,Jack Hawksworth,Vasser Sullivan,Lexus RC F GT3,50,1:30:45.123,,1:35.678,160.5,Running
2,3,Jan Heylen,Wright Motorsports,Porsche 911 GT3 R,50,1:30:50.456,+5.333,1:36.123,159.8,Running
```

### Interpreting Analytics

**Data View Tab**:
- Browse raw and processed data
- New columns ending in `_SEC` show time in seconds
- Sort by clicking column headers

**Dashboard Tab** (Future):
- View lap time progression charts
- Analyze gap evolution
- Identify anomalies with red markers

---

## Development & Testing

### Running the Test Suite

**Full Test Suite with Coverage**:
```bash
pytest --cov=src tests/
```

**Run Specific Test File**:
```bash
pytest tests/test_loader.py -v
```

**Generate HTML Coverage Report**:
```bash
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html
```

### Code Quality Standards

**PEP 8 Compliance**:
All code follows PEP 8 style guidelines, enforced by `flake8`:
```bash
flake8 src/ tests/
```

**Automated Formatting**:
We use `black` for consistent code formatting:
```bash
black src/ tests/
```

**Docstring Standards**:
All modules, classes, and functions include PEP 257 compliant docstrings with:
- Description of purpose
- Parameter types and descriptions
- Return value types
- Example usage (where applicable)

### Continuous Integration

**GitHub Actions Workflow** (`.github/workflows/ci.yml`):
- Runs on every push and pull request
- Tests across Python 3.8, 3.9, and 3.10
- Executes linting and full test suite
- Fails if any test fails or linting errors exist

---

## Deliverables & Verification

### Core Components Implemented

✅ **Data Loader** (`src/core/data_loader.py`)
- CSV parsing with error handling
- Time format conversion (HH:MM:SS.sss, MM:SS.sss, +SS.sss)
- Data cleaning and standardization

✅ **AI Models** (`src/ai/models.py`)
- `LapTimePredictor` - LSTM-based prediction (mocked)
- `AnomalyDetector` - Isolation Forest implementation
- `RaceCoach` - Performance insight generator

✅ **User Interface** (`src/ui/main_window.py`)
- Main window with tabbed layout
- CSV import functionality
- Data table display

✅ **Test Suite** (`tests/`)
- Unit tests for data loader
- Unit tests for AI models
- 79% code coverage

✅ **Documentation**
- Comprehensive README
- Contributing guidelines
- API documentation (MkDocs)
- CI/CD pipeline

### Verification Steps

1. **Test Data Loading**:
   ```bash
   python tests/test_loader.py
   ```
   Expected: All assertions pass, time conversions correct

2. **Test AI Models**:
   ```bash
   python tests/test_ai.py
   ```
   Expected: Model shapes correct, predictions generated

3. **Launch Application**:
   ```bash
   python src/main.py
   ```
   Expected: Window opens, CSV import works

4. **Build Documentation**:
   ```bash
   mkdocs build
   ```
   Expected: Site generated in `site/` directory

### Extending the Project

**Adding New Features**:
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement with tests and docstrings
3. Run test suite: `pytest --cov=src tests/`
4. Format code: `black src/`
5. Submit pull request

**Adding New AI Models**:
1. Add model class to `src/ai/models.py`
2. Include PEP 257 docstrings
3. Create unit tests in `tests/test_ai.py`
4. Update documentation

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request workflow
- Issue reporting process

**Quick Contribution Checklist**:
- [ ] Code follows PEP 8 (verified with `flake8 src/ tests/`)
- [ ] All functions have docstrings (PEP 257 compliant)
- [ ] Tests added for new features
- [ ] All tests pass (`pytest --cov=src tests/`)
- [ ] Code formatted with `black src/ tests/`
- [ ] Documentation updated if needed

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Telemetry Analysis Tool Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Acknowledgments

**Third-Party Libraries**:
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [NumPy](https://numpy.org/) - Numerical computing
- [Scikit-learn](https://scikit-learn.org/) - Machine learning
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Matplotlib](https://matplotlib.org/) - Visualization
- [MkDocs](https://www.mkdocs.org/) - Documentation

**Inspiration**:
- Toyota Racing telemetry format specification
- Motorsport data analysis best practices

---

## Support & Contact

For questions, issues, or feature requests:
- **GitHub Issues**: [Create an issue](https://github.com/ch2aitanya/telemetry-analysis-tool/issues)
- **Documentation**: [Read the docs](https://yourusername.github.io/telemetry-analysis-tool/)
- **Email**: ChaitanyaNehe@outlook.com
