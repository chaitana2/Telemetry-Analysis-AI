# Architecture Overview

This document describes the high-level architecture of the Telemetry Analysis Tool.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (PyQt6)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Main Window │  │  Data View   │  │  Dashboard   │     │
│  │              │  │    Tab       │  │     Tab      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Data Module                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              DataLoader Class                        │  │
│  │  • load_csv()      • parse_time_str()               │  │
│  │  • preprocess()    • clean_data()                   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Analysis Module                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ LapTime      │  │  Anomaly     │  │  Race        │     │
│  │ Predictor    │  │  Detector    │  │  Coach       │     │
│  │ (LSTM)       │  │ (IsoForest)  │  │ (Insights)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer (`src/ui/`)

**MainWindow** (`main_window.py`)
- Manages application lifecycle
- Handles user interactions
- Coordinates data flow between components

**Responsibilities:**
- CSV file selection and import
- Display processed data in table format
- Render visualizations (future)

### 2. Core Data Layer (`src/core/`)

**DataLoader** (`data_loader.py`)
- Ingests Toyota-format CSV files
- Cleans and preprocesses telemetry data
- Converts time formats to numeric values

**Data Flow:**
1. Raw CSV → `load_csv()`
2. Validation → `preprocess()`
3. Time conversion → `parse_time_str()`
4. Clean DataFrame → returned to UI

### 3. AI Analysis Layer (`src/ai/`)

**LapTimePredictor** (`models.py`)
- LSTM neural network for lap time forecasting
- Input: Historical lap data (position, gaps, times)
- Output: Predicted next lap time

**AnomalyDetector** (`models.py`)
- Isolation Forest for outlier detection
- Input: Multi-dimensional telemetry features
- Output: Anomaly flags (-1 for outliers)

**RaceCoach** (`models.py`)
- Performance analysis and insights
- Input: Driver-specific telemetry
- Output: Textual coaching recommendations

## Data Flow

```
CSV File
   ↓
DataLoader.load_csv()
   ↓
DataLoader.preprocess()
   ↓
Clean DataFrame
   ↓
   ├─→ UI Display (MainWindow)
   ├─→ LapTimePredictor.forward()
   ├─→ AnomalyDetector.predict()
   └─→ RaceCoach.analyze_driver()
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | PyQt6 | Cross-platform desktop interface |
| Data Processing | Pandas, NumPy | DataFrame manipulation |
| AI/ML | Scikit-learn | Anomaly detection |
| AI/ML (Future) | PyTorch | Deep learning (LSTM) |
| Visualization | Matplotlib | Charts and graphs |
| Testing | Pytest | Unit and integration tests |
| Documentation | MkDocs | API documentation |
| CI/CD | GitHub Actions | Automated testing |

## Design Patterns

### 1. **Separation of Concerns**
- UI, Data, and AI layers are independent
- Each module has a single responsibility

### 2. **Dependency Injection**
- DataLoader is injected into MainWindow
- AI models receive preprocessed data

### 3. **Factory Pattern** (Future)
- Model factory for creating different AI analyzers

## Extension Points

### Adding New AI Models
1. Create new class in `src/ai/models.py`
2. Implement required interface (train, predict)
3. Add unit tests in `tests/test_ai.py`
4. Integrate into UI workflow

### Adding New Data Sources
1. Extend DataLoader with new parser method
2. Add format detection logic
3. Update tests with new format examples

### Adding Visualizations
1. Create new tab in MainWindow
2. Use Matplotlib for plotting
3. Connect to processed data

## Security Considerations

- **Input Validation**: All CSV inputs are validated
- **Error Handling**: Graceful degradation on malformed data
- **No External Calls**: Fully offline operation
- **Data Privacy**: No telemetry data leaves the user's machine

## Performance

- **CSV Loading**: O(n) where n = number of rows
- **Time Parsing**: O(n) per column
- **Anomaly Detection**: O(n log n) for Isolation Forest
- **Memory**: Scales linearly with dataset size

## Future Architecture

### Planned Enhancements
- **Backend API**: FastAPI server for remote processing
- **Database**: SQLite for session storage
- **Real-time**: WebSocket for live telemetry
- **Mobile**: Flutter app consuming API
