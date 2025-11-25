# Testing Guide for Telemetry Analysis Tool

This guide provides comprehensive instructions for testing the application at various levels.

---

## Table of Contents

1. [Quick Testing](#quick-testing)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [Manual Testing](#manual-testing)
5. [Test Coverage](#test-coverage)
6. [Writing New Tests](#writing-new-tests)
7. [Continuous Integration](#continuous-integration)

---

## Quick Testing

### Run All Tests

The fastest way to verify everything works:

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Run all tests
pytest tests/
```

**Expected Output:**
```
============ test session starts ============
collected 6 items

tests/test_ai.py .                    [ 16%]
tests/test_integration.py ....        [ 83%]
tests/test_loader.py .                [100%]

============= 6 passed in 1.42s =============
```

---

## Unit Testing

### Test Data Loader

Tests CSV parsing, time format conversion, and data preprocessing:

```bash
pytest tests/test_loader.py -v
```

**What's tested:**
- ✅ CSV file loading
- ✅ Time string parsing (HH:MM:SS.sss, MM:SS.sss, +SS.sss)
- ✅ Data preprocessing and cleaning
- ✅ Column standardization

**Example test:**
```python
def test_loader():
    """Test DataLoader functionality."""
    loader = DataLoader()
    assert loader.load_csv("tests/test_data.csv") is True
    df = loader.preprocess()
    assert df is not None
    assert 'TOTAL_TIME_SEC' in df.columns
```

### Test AI Models

Tests anomaly detection and race coach functionality:

```bash
pytest tests/test_ai.py -v
```

**What's tested:**
- ✅ Anomaly detector training and prediction
- ✅ Lap time predictor (mocked)
- ✅ Race coach analysis

**Example test:**
```python
def test_ai():
    """Test AI models."""
    # Test Anomaly Detector
    detector = AnomalyDetector()
    data = np.random.rand(100, 3)
    detector.train(data)
    predictions = detector.predict(data)
    assert predictions.shape[0] == 100
```

---

## Integration Testing

### End-to-End Workflow Tests

Tests complete data processing pipeline:

```bash
pytest tests/test_integration.py -v
```

**What's tested:**
- ✅ Load CSV → Preprocess → Analyze workflow
- ✅ Anomaly detection on realistic data
- ✅ Missing value handling
- ✅ Malformed time string parsing

**Test scenarios:**
1. **Complete Workflow**: CSV load → preprocessing → AI analysis
2. **Outlier Detection**: Identifies unusual lap times
3. **Data Quality**: Handles missing/malformed data gracefully

---

## Manual Testing

### 1. Application Launch Test

**Objective**: Verify the application starts correctly

**Steps:**
1. Run the launcher:
   ```bash
   ./run.sh  # or run-macos.sh, run.bat
   ```
2. Verify the main window opens
3. Check that both tabs are visible: "Data View" and "Dashboard"

**Expected Result:**
- Window opens without errors
- UI is responsive
- Both tabs are accessible

### 2. CSV Import Test

**Objective**: Test CSV file import functionality

**Steps:**
1. Launch the application
2. Click "Import CSV" button
3. Select `tests/test_data.csv`
4. Verify data appears in the Data View tab

**Expected Result:**
- File dialog opens
- Data loads successfully
- Table displays all rows and columns
- Time columns show converted values (with `_SEC` suffix)

**Sample Test Data:**
```csv
POSITION,NUMBER,DRIVER,TEAM,VEHICLE,LAPS,TOTAL_TIME,GAP_FIRST,FL_TIME,FL_KPH,STATUS
1,14,Jack Hawksworth,Vasser Sullivan,Lexus RC F GT3,50,1:30:45.123,,1:35.678,160.5,Running
2,3,Jan Heylen,Wright Motorsports,Porsche 911 GT3 R,50,1:30:50.456,+5.333,1:36.123,159.8,Running
```

### 3. Data Processing Test

**Objective**: Verify data preprocessing works correctly

**Steps:**
1. Import a CSV file
2. Check the Data View tab
3. Verify new columns exist:
   - `TOTAL_TIME_SEC`
   - `GAP_FIRST_SEC`
   - `FL_TIME_SEC`

**Expected Result:**
- Time strings converted to seconds
- Original columns preserved
- No data loss

### 4. Error Handling Test

**Objective**: Test application behavior with invalid data

**Test Cases:**

**A. Invalid CSV Format:**
1. Create a CSV with missing required columns
2. Try to import it
3. Verify error message appears

**B. Malformed Time Strings:**
1. Create CSV with invalid time formats
2. Import and verify NaN values are handled

**C. Empty File:**
1. Try to import an empty CSV
2. Verify graceful error handling

---

## Test Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=src tests/

# Generate HTML report
pytest --cov=src --cov-report=html tests/

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Current Coverage

```
Name                      Stmts   Miss  Cover
---------------------------------------------
src/ai/models.py             41      4    90%
src/core/data_loader.py      55      5    91%
src/main.py                  13     13     0%
---------------------------------------------
TOTAL                       109     22    80%
```

**Coverage Goals:**
- ✅ Overall: 80%+ (achieved)
- ✅ Core modules: 90%+ (achieved)
- ⚠️ UI module: Not tested (requires GUI testing framework)

---

## Writing New Tests

### Test Structure

Follow this pattern for new tests:

```python
import pytest
from src.module import ClassName

class TestClassName:
    """Test suite for ClassName."""
    
    def test_feature_name(self):
        """Test specific feature."""
        # Arrange
        obj = ClassName()
        
        # Act
        result = obj.method()
        
        # Assert
        assert result == expected_value
```

### Using Fixtures

For reusable test data:

```python
@pytest.fixture
def sample_data(tmp_path):
    """Create sample CSV for testing."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("POSITION,NUMBER\n1,14\n2,3\n")
    return str(csv_file)

def test_with_fixture(sample_data):
    """Test using fixture."""
    loader = DataLoader()
    assert loader.load_csv(sample_data) is True
```

### Parametrized Tests

For testing multiple inputs:

```python
@pytest.mark.parametrize("input_str,expected", [
    ("1:35.678", 95.678),
    ("+5.234", 5.234),
    ("+1:14.985", 74.985),
])
def test_parse_time_formats(input_str, expected):
    """Test various time formats."""
    loader = DataLoader()
    result = loader.parse_time_str(input_str)
    assert result == pytest.approx(expected, rel=1e-3)
```

---

## Continuous Integration

### GitHub Actions

Tests run automatically on every push and pull request.

**Workflow:** `.github/workflows/ci.yml`

**What runs:**
1. Linting with `flake8`
2. Full test suite with `pytest`
3. Code coverage reporting
4. Multi-version testing (Python 3.8, 3.9, 3.10)

**View Results:**
- Go to GitHub repository
- Click "Actions" tab
- View latest workflow run

**Status Badge:**
Add to README:
```markdown
![Tests](https://github.com/chaitana2/Telemetry-Analysis-AI/workflows/CI/badge.svg)
```

---

## Troubleshooting Tests

### Tests Fail to Run

**Problem:** `pytest: command not found`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall pytest
pip install pytest pytest-cov
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
```bash
# Run from project root directory
cd /path/to/Telemetry-Analysis-AI

# Or set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:.
```

### Tests Pass Locally but Fail in CI

**Common causes:**
- Different Python versions
- Missing dependencies in `requirements.txt`
- Platform-specific code

**Solution:**
- Test with multiple Python versions locally
- Verify all dependencies are listed
- Use platform-agnostic code

---

## Best Practices

### ✅ Do's

- Write tests before fixing bugs (TDD)
- Keep tests simple and focused
- Use descriptive test names
- Test edge cases and error conditions
- Maintain high coverage (80%+)
- Run tests before committing

### ❌ Don'ts

- Don't test external libraries
- Don't write tests that depend on external services
- Don't skip tests (use `@pytest.mark.skip` with reason)
- Don't commit failing tests
- Don't test implementation details

---

## Quick Reference

### Common Commands

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_loader.py

# Run specific test
pytest tests/test_loader.py::test_loader

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Run and stop on first failure
pytest tests/ -x

# Run only failed tests from last run
pytest --lf

# Show print statements
pytest tests/ -s
```

### Test Markers

```bash
# Run only integration tests
pytest tests/ -m integration

# Skip slow tests
pytest tests/ -m "not slow"
```

---

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Project CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Support

If you encounter testing issues:
- Check [GitHub Issues](https://github.com/chaitana2/Telemetry-Analysis-AI/issues)
- Review [CONTRIBUTING.md](../CONTRIBUTING.md)
- Ask in [Discussions](https://github.com/chaitana2/Telemetry-Analysis-AI/discussions)
