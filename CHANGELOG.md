# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-25

### Added
- Core `DataLoader` for parsing and preprocessing Toyota telemetry CSVs
- Time format conversion supporting HH:MM:SS.sss, MM:SS.sss, and +SS.sss formats
- AI module containing `LapTimePredictor` (LSTM - mocked), `AnomalyDetector` (Isolation Forest), and `RaceCoach`
- PyQt6 `MainWindow` with CSV import functionality and tabbed data view
- Comprehensive unit tests for data loading and AI models (79% coverage)
- Integration tests for end-to-end workflow validation
- Complete project documentation:
  - Detailed README.md with feature descriptions and usage instructions
  - CONTRIBUTING.md with development workflow and code standards
  - PEP 257 compliant docstrings across all modules
  - MkDocs configuration for API documentation
- GitHub Actions CI/CD pipeline for automated testing
- MIT License
- .gitignore for Python projects
- Example docstring template for contributors

### Fixed
- Time parsing to support hour-long race durations (HH:MM:SS format)
- RaceCoach analysis threshold adjusted for smaller datasets

### Documentation
- Comprehensive README with AI model explanations
- Detailed setup and installation instructions
- Development and testing guidelines
- Contribution workflow with examples
- API documentation generated via MkDocs
