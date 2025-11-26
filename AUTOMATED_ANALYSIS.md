# Automated Analysis Pipeline

This project now includes a fully automated analysis pipeline that handles data conversion, analysis, and report generation.

## Features

1.  **Auto Data Conversion**:
    *   Automatically detects CSV schema (delimiter, encoding).
    *   Cleans data (handles missing values, outliers).
    *   Converts units (time strings to seconds, etc.).
    *   Generates derived features.

2.  **Automated Analysis**:
    *   **Anomaly Detection**: Identifies unusual lap times or telemetry data.
    *   **Driver Coaching**: Provides specific insights for each driver (braking points, consistency).
    *   **Summary Statistics**: Calculates overall race stats.

3.  **Automated Report Generation**:
    *   Generates a professional PDF report.
    *   Includes summary tables, anomaly details, and coaching insights.

## Usage

### Command Line Interface

You can run the analysis using the `run_analysis.py` script:

```bash
# Process a single file
python run_analysis.py data/raw/my_race_data.csv

# Process a single file and specify output directory
python run_analysis.py data/raw/my_race_data.csv --output reports/

# Process all CSV files in a directory
python run_analysis.py data/raw/
```

### Python API

You can also use the pipeline in your own scripts:

```python
from src.automated_analysis import AutomatedPipeline

pipeline = AutomatedPipeline()

# Process a file
pipeline.process_file("data/raw/race.csv")

# Process a directory
pipeline.process_directory("data/raw/")
```

## Output

The pipeline generates PDF reports named `Report_<filename>_<timestamp>.pdf` in the specified output directory (or the same directory as the input file by default).
