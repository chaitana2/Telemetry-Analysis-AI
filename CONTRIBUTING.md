# Contributing to Telemetry Analysis Tool

Thank you for your interest in contributing! This guide will help you understand our development process and quality standards.

---

## Code of Conduct

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct. By participating, you are expected to:
- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards other contributors

---

## How to Contribute

### Reporting Bugs

**Before Submitting**:
1. Check the [issue tracker](https://github.com/chaitana2/Telemetry-Analysis-AI/issues) for existing reports
2. Verify the bug exists in the latest version
3. Collect relevant information (OS, Python version, error messages)

**Bug Report Template**:
```markdown
**Description**: Brief description of the bug

**Steps to Reproduce**:
1. Step one
2. Step two
3. Expected vs. actual behavior

**Environment**:
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.10.5]
- Package Versions: [run `pip freeze`]

**Error Messages**:
```
Paste error traceback here
```

**Additional Context**: Screenshots, CSV samples, etc.
```

### Suggesting Features

We welcome feature suggestions! Please:
1. Check if the feature has been requested
2. Explain the use case and benefit
3. Provide examples of how it would work
4. Consider implementation complexity

---

## Development Workflow

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/Telemetry-Analysis-AI.git
cd Telemetry-Analysis-AI
git remote add upstream https://github.com/chaitana2/Telemetry-Analysis-AI.git
```

### 2. Create a Branch

```bash
# Feature branch
git checkout -b feature/add-lap-comparison

# Bug fix branch
git checkout -b fix/time-parsing-error

# Documentation branch
git checkout -b docs/update-readme
```

### 3. Set Up Development Environment

```bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

### 4. Make Changes

**Code Quality Checklist**:
- [ ] Follow PEP 8 style guidelines
- [ ] Add type hints to function signatures
- [ ] Write comprehensive docstrings
- [ ] Include unit tests for new code
- [ ] Update documentation if needed

### 5. Test Your Changes

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_loader.py -v

# Check code style
flake8 src/ tests/

# Format code
black src/ tests/
```

### 6. Commit Changes

**Commit Message Format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example**:
```
feat: Add lap-to-lap comparison visualization

Implemented a new chart in the Dashboard tab that overlays
lap times for multiple drivers, allowing direct comparison.

Closes #42
```

### 7. Push and Create Pull Request

```bash
git push origin feature/add-lap-comparison
```

Then create a pull request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots/examples if applicable

---

## Coding Standards

### PEP 8 Compliance

All code must follow [PEP 8](https://pep8.org/) guidelines:
- 4 spaces for indentation (no tabs)
- Maximum line length: 127 characters
- Two blank lines between top-level functions/classes
- Descriptive variable names (no single letters except loop counters)

**Automated Checking**:
```bash
flake8 src/ tests/ --max-line-length=127
```

### Code Formatting with Black

We use [Black](https://black.readthedocs.io/) for consistent formatting:

```bash
# Format all files
black src/ tests/

# Check without modifying
black --check src/ tests/
```

### Type Hints

Use type hints for all function parameters and return values:

```python
from typing import Optional, List
import pandas as pd

def process_telemetry(filepath: str, validate: bool = True) -> Optional[pd.DataFrame]:
    """
    Process telemetry CSV file.
    
    Args:
        filepath (str): Absolute path to CSV file.
        validate (bool): Whether to validate data integrity.
    
    Returns:
        Optional[pd.DataFrame]: Processed dataframe or None if error.
    """
    # Implementation
    pass
```

### Docstring Standards (PEP 257)

**Module Docstring**:
```python
"""
Telemetry data loading and preprocessing module.

This module provides the DataLoader class for ingesting Toyota-format
CSV files and converting them into analysis-ready dataframes.
"""
```

**Class Docstring**:
```python
class DataLoader:
    """
    Handles loading and preprocessing of telemetry data from CSV files.

    The DataLoader supports Toyota's official telemetry format and automatically
    converts time strings to numeric values for analysis.

    Attributes:
        raw_data (Optional[pd.DataFrame]): The raw data loaded from CSV.
        clean_data (Optional[pd.DataFrame]): The processed and cleaned data.

    Example:
        >>> loader = DataLoader()
        >>> loader.load_csv("telemetry.csv")
        >>> df = loader.preprocess()
        >>> print(df.head())
    """
```

**Function Docstring**:
```python
def parse_time_str(self, time_str: str) -> float:
    """
    Converts time strings to seconds.

    Supports multiple formats:
    - HH:MM:SS.sss (e.g., "1:30:45.123")
    - MM:SS.sss (e.g., "1:35.678")
    - +SS.sss (gap format, e.g., "+5.234")

    Args:
        time_str (str): The time string to parse.

    Returns:
        float: The time in seconds, or np.nan if parsing fails.

    Raises:
        ValueError: If time_str format is unrecognized.

    Example:
        >>> loader = DataLoader()
        >>> loader.parse_time_str("1:30:45.123")
        5445.123
        >>> loader.parse_time_str("+5.234")
        5.234
    """
```

---

## Testing Requirements

### Test Coverage Goals

- **Minimum**: 80% overall coverage
- **Critical modules**: 90%+ coverage (data_loader, models)
- **New features**: Must include tests

### Writing Tests

**Test Structure**:
```python
import pytest
from src.core.data_loader import DataLoader

class TestDataLoader:
    """Test suite for DataLoader class."""
    
    def test_load_csv_success(self, tmp_path):
        """Test successful CSV loading."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("POSITION,NUMBER\n1,14\n2,3\n")
        loader = DataLoader()
        
        # Act
        result = loader.load_csv(str(csv_file))
        
        # Assert
        assert result is True
        assert loader.raw_data is not None
        assert len(loader.raw_data) == 2
    
    def test_parse_time_str_hhmmss(self):
        """Test parsing HH:MM:SS.sss format."""
        loader = DataLoader()
        result = loader.parse_time_str("1:30:45.123")
        assert result == pytest.approx(5445.123, rel=1e-3)
    
    @pytest.mark.parametrize("input_str,expected", [
        ("1:35.678", 95.678),
        ("+5.234", 5.234),
        ("+1:14.985", 74.985),
    ])
    def test_parse_time_str_formats(self, input_str, expected):
        """Test various time string formats."""
        loader = DataLoader()
        result = loader.parse_time_str(input_str)
        assert result == pytest.approx(expected, rel=1e-3)
```

**Running Tests**:
```bash
# All tests
pytest

# Specific test class
pytest tests/test_loader.py::TestDataLoader

# Specific test method
pytest tests/test_loader.py::TestDataLoader::test_load_csv_success

# With coverage
pytest --cov=src --cov-report=term-missing tests/
```

---

## Pull Request Process

### Before Submitting

1. **Update Documentation**:
   - Add docstrings to new code
   - Update README if adding features
   - Update CHANGELOG.md

2. **Run Full Test Suite**:
   ```bash
   pytest --cov=src tests/
   flake8 src/ tests/
   black --check src/ tests/
   ```

3. **Update Dependencies**:
   If you added packages:
   ```bash
   pip freeze > requirements.txt
   ```

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added tests for new features
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows PEP 8
- [ ] Docstrings added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Code Review Process

1. **Automated Checks**: CI pipeline must pass
2. **Peer Review**: At least one maintainer approval required
3. **Feedback**: Address review comments promptly
4. **Merge**: Squash and merge to main branch

---

## Continuous Integration

Our CI pipeline (`.github/workflows/ci.yml`) runs on every push:

**Checks Performed**:
- Linting with `flake8`
- Full test suite with `pytest`
- Code coverage reporting
- Multi-version testing (Python 3.8, 3.9, 3.10)

**Viewing Results**:
- Check the "Actions" tab on GitHub
- Green checkmark = all tests passed
- Red X = failures (click for details)

---

## Development Tips

### Setting Up Pre-Commit Hooks

Automate code quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

# Install hooks
pre-commit install
```

### Debugging Tips

**Enable Verbose Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Interactive Testing**:
```bash
python -i src/core/data_loader.py
>>> loader = DataLoader()
>>> loader.load_csv("tests/test_data.csv")
```

---

## Questions?

- **GitHub Discussions**: For general questions
- **Issue Tracker**: For bug reports and feature requests
- **Email**: maintainers@example.com

Thank you for contributing! 🎉
