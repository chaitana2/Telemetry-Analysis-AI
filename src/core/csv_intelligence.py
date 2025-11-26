"""
CSV Intelligence Module - AI-powered CSV analysis and schema detection.

This module provides intelligent analysis of CSV files including automatic
schema detection, column type inference, and data quality assessment.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass
import chardet


class ColumnType(Enum):
    """Enumeration of detected column types."""
    TIME = "time"
    SPEED = "speed"
    POSITION = "position"
    LAP_NUMBER = "lap_number"
    DISTANCE = "distance"
    TEMPERATURE = "temperature"
    DRIVER_NAME = "driver_name"
    TEAM_NAME = "team_name"
    VEHICLE = "vehicle"
    STATUS = "status"
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class ColumnInfo:
    """Information about a detected column."""
    name: str
    detected_type: ColumnType
    confidence: float
    sample_values: List[Any]
    missing_count: int
    missing_percentage: float
    unique_count: int
    data_type: str
    patterns: List[str]


@dataclass
class SchemaAnalysis:
    """Complete schema analysis results."""
    columns: Dict[str, ColumnInfo]
    total_rows: int
    total_columns: int
    overall_quality_score: float
    delimiter: str
    encoding: str
    has_header: bool
    suggested_mappings: Dict[str, str]
    warnings: List[str]


class ColumnTypeClassifier:
    """
    Classifies column types using pattern matching and statistical analysis.
    """
    
    # Pattern definitions for different column types
    TIME_PATTERNS = [
        r'\d{1,2}:\d{2}:\d{2}\.?\d*',  # HH:MM:SS.sss
        r'\d{1,2}:\d{2}\.?\d*',         # MM:SS.sss
        r'\+?\d+\.?\d*',                 # +SS.sss
    ]
    
    SPEED_KEYWORDS = ['speed', 'velocity', 'kph', 'mph', 'km/h', 'kmh', 'vel']
    POSITION_KEYWORDS = ['position', 'pos', 'rank', 'place']
    LAP_KEYWORDS = ['lap', 'laps']
    DISTANCE_KEYWORDS = ['distance', 'dist', 'km', 'mile', 'meter']
    TEMP_KEYWORDS = ['temp', 'temperature', 'deg', 'celsius', 'fahrenheit']
    DRIVER_KEYWORDS = ['driver', 'pilot', 'racer', 'name']
    TEAM_KEYWORDS = ['team', 'constructor', 'squad']
    VEHICLE_KEYWORDS = ['vehicle', 'car', 'model']
    STATUS_KEYWORDS = ['status', 'state', 'condition']
    
    def __init__(self):
        """Initialize the classifier."""
        pass
    
    def classify_column(self, column_name: str, series: pd.Series) -> Tuple[ColumnType, float]:
        """
        Classify a column based on name and data patterns.
        
        Args:
            column_name (str): Name of the column.
            series (pd.Series): Column data.
        
        Returns:
            Tuple[ColumnType, float]: Detected type and confidence score (0-1).
        """
        column_name_lower = column_name.lower()
        
        # Check for time columns
        if self._matches_keywords(column_name_lower, ['time', 'gap', 'total']):
            if self._matches_time_patterns(series):
                return ColumnType.TIME, 0.9
        
        # Check for speed columns
        if self._matches_keywords(column_name_lower, self.SPEED_KEYWORDS):
            if self._is_numeric_range(series, 0, 500):  # Reasonable speed range
                return ColumnType.SPEED, 0.95
        
        # Check for position columns
        if self._matches_keywords(column_name_lower, self.POSITION_KEYWORDS):
            if self._is_integer_range(series, 1, 100):  # Reasonable position range
                return ColumnType.POSITION, 0.95
        
        # Check for lap number columns
        if self._matches_keywords(column_name_lower, self.LAP_KEYWORDS):
            if self._is_integer_range(series, 0, 1000):
                return ColumnType.LAP_NUMBER, 0.9
        
        # Check for distance columns
        if self._matches_keywords(column_name_lower, self.DISTANCE_KEYWORDS):
            if self._is_numeric(series):
                return ColumnType.DISTANCE, 0.85
        
        # Check for temperature columns
        if self._matches_keywords(column_name_lower, self.TEMP_KEYWORDS):
            if self._is_numeric_range(series, -50, 200):
                return ColumnType.TEMPERATURE, 0.9
        
        # Check for driver name columns
        if self._matches_keywords(column_name_lower, self.DRIVER_KEYWORDS):
            if self._is_text_with_names(series):
                return ColumnType.DRIVER_NAME, 0.9
        
        # Check for team name columns
        if self._matches_keywords(column_name_lower, self.TEAM_KEYWORDS):
            if self._is_text(series):
                return ColumnType.TEAM_NAME, 0.85
        
        # Check for vehicle columns
        if self._matches_keywords(column_name_lower, self.VEHICLE_KEYWORDS):
            if self._is_text(series):
                return ColumnType.VEHICLE, 0.85
        
        # Check for status columns
        if self._matches_keywords(column_name_lower, self.STATUS_KEYWORDS):
            if self._is_categorical(series):
                return ColumnType.STATUS, 0.9
        
        # Generic classification based on data type
        if self._is_numeric(series):
            return ColumnType.NUMERIC, 0.5
        elif self._is_categorical(series):
            return ColumnType.CATEGORICAL, 0.5
        elif self._is_text(series):
            return ColumnType.TEXT, 0.5
        
        return ColumnType.UNKNOWN, 0.3
    
    def _matches_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords."""
        return any(keyword in text for keyword in keywords)
    
    def _matches_time_patterns(self, series: pd.Series) -> bool:
        """Check if series matches time patterns."""
        sample = series.dropna().astype(str).head(10)
        if len(sample) == 0:
            return False
        
        matches = 0
        for value in sample:
            for pattern in self.TIME_PATTERNS:
                if re.match(pattern, value.strip()):
                    matches += 1
                    break
        
        return matches / len(sample) > 0.5
    
    def _is_numeric(self, series: pd.Series) -> bool:
        """Check if series is numeric."""
        try:
            pd.to_numeric(series.dropna(), errors='raise')
            return True
        except:
            return False
    
    def _is_numeric_range(self, series: pd.Series, min_val: float, max_val: float) -> bool:
        """Check if series is numeric within a range."""
        try:
            numeric = pd.to_numeric(series.dropna(), errors='coerce')
            if len(numeric) == 0:
                return False
            return numeric.between(min_val, max_val).mean() > 0.7
        except:
            return False
    
    def _is_integer_range(self, series: pd.Series, min_val: int, max_val: int) -> bool:
        """Check if series contains integers within a range."""
        try:
            numeric = pd.to_numeric(series.dropna(), errors='coerce')
            if len(numeric) == 0:
                return False
            is_int = (numeric == numeric.astype(int)).mean() > 0.9
            in_range = numeric.between(min_val, max_val).mean() > 0.7
            return is_int and in_range
        except:
            return False
    
    def _is_text(self, series: pd.Series) -> bool:
        """Check if series contains text."""
        return series.dtype == 'object' or series.dtype.name == 'string'
    
    def _is_text_with_names(self, series: pd.Series) -> bool:
        """Check if series contains name-like text."""
        if not self._is_text(series):
            return False
        sample = series.dropna().astype(str).head(10)
        # Names typically have spaces or capital letters
        name_pattern = r'^[A-Z][a-z]+(\s[A-Z][a-z]+)*$'
        matches = sum(1 for val in sample if re.match(name_pattern, val.strip()))
        return matches / len(sample) > 0.5 if len(sample) > 0 else False
    
    def _is_categorical(self, series: pd.Series) -> bool:
        """Check if series is categorical (low cardinality)."""
        unique_ratio = series.nunique() / len(series) if len(series) > 0 else 0
        return unique_ratio < 0.1 and series.nunique() < 20


class DataQualityAssessor:
    """
    Assesses data quality of CSV files.
    """
    
    def __init__(self):
        """Initialize the assessor."""
        pass
    
    def assess_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Assess overall data quality.
        
        Args:
            df (pd.DataFrame): DataFrame to assess.
        
        Returns:
            Dict[str, Any]: Quality metrics.
        """
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isna().sum().sum()
        missing_percentage = (missing_cells / total_cells * 100) if total_cells > 0 else 0
        
        # Calculate completeness score (0-100)
        completeness_score = 100 - missing_percentage
        
        # Calculate consistency score based on data types
        consistency_score = self._calculate_consistency(df)
        
        # Overall quality score (weighted average)
        overall_score = (completeness_score * 0.6 + consistency_score * 0.4)
        
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'total_cells': total_cells,
            'missing_cells': missing_cells,
            'missing_percentage': missing_percentage,
            'completeness_score': completeness_score,
            'consistency_score': consistency_score,
            'overall_quality_score': overall_score,
            'columns_with_missing': df.columns[df.isna().any()].tolist(),
            'duplicate_rows': df.duplicated().sum()
        }
    
    def _calculate_consistency(self, df: pd.DataFrame) -> float:
        """Calculate data consistency score."""
        scores = []
        
        for col in df.columns:
            # Check if column has consistent data type
            non_null = df[col].dropna()
            if len(non_null) == 0:
                continue
            
            # Try to convert to numeric
            try:
                pd.to_numeric(non_null, errors='raise')
                scores.append(100)  # Fully consistent numeric
            except:
                # Check string consistency
                if non_null.dtype == 'object':
                    # Check if values have similar patterns
                    unique_ratio = non_null.nunique() / len(non_null)
                    if unique_ratio < 0.5:
                        scores.append(80)  # Categorical-like
                    else:
                        scores.append(60)  # Free text
                else:
                    scores.append(70)
        
        return np.mean(scores) if scores else 50


class CSVSchemaAnalyzer:
    """
    Main class for intelligent CSV schema analysis.
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.classifier = ColumnTypeClassifier()
        self.quality_assessor = DataQualityAssessor()
    
    def analyze_file(self, filepath: str, sample_rows: int = 100) -> SchemaAnalysis:
        """
        Analyze a CSV file and detect its schema.
        
        Args:
            filepath (str): Path to CSV file.
            sample_rows (int): Number of rows to sample for analysis.
        
        Returns:
            SchemaAnalysis: Complete analysis results.
        """
        # Detect encoding
        encoding = self._detect_encoding(filepath)
        
        # Detect delimiter
        delimiter = self._detect_delimiter(filepath, encoding)
        
        # Load sample data
        try:
            df = pd.read_csv(filepath, encoding=encoding, delimiter=delimiter, nrows=sample_rows)
            has_header = True
        except:
            # Try without header
            df = pd.read_csv(filepath, encoding=encoding, delimiter=delimiter, 
                           nrows=sample_rows, header=None)
            has_header = False
        
        # Analyze columns
        columns_info = {}
        for col in df.columns:
            col_info = self._analyze_column(col, df[col])
            columns_info[str(col)] = col_info
        
        # Assess data quality
        quality_metrics = self.quality_assessor.assess_quality(df)
        
        # Generate suggested mappings
        suggested_mappings = self._generate_mappings(columns_info)
        
        # Generate warnings
        warnings = self._generate_warnings(columns_info, quality_metrics)
        
        return SchemaAnalysis(
            columns=columns_info,
            total_rows=quality_metrics['total_rows'],
            total_columns=quality_metrics['total_columns'],
            overall_quality_score=quality_metrics['overall_quality_score'],
            delimiter=delimiter,
            encoding=encoding,
            has_header=has_header,
            suggested_mappings=suggested_mappings,
            warnings=warnings
        )
    
    def _detect_encoding(self, filepath: str) -> str:
        """Detect file encoding."""
        with open(filepath, 'rb') as f:
            result = chardet.detect(f.read(10000))
        return result['encoding'] or 'utf-8'
    
    def _detect_delimiter(self, filepath: str, encoding: str) -> str:
        """
        Detect CSV delimiter by analyzing multiple lines.
        
        Improved to handle:
        - Semicolon delimiters
        - Headers with no delimiters
        - Mixed delimiters
        """
        try:
            with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                # Read first 5 lines for better detection
                lines = [f.readline() for _ in range(5)]
            
            # Remove empty lines
            lines = [line for line in lines if line.strip()]
            
            if not lines:
                return ','  # Default
            
            # Count potential delimiters across all lines
            delimiters = {',': 0, ';': 0, '\t': 0, '|': 0}
            
            for line in lines:
                for delim in delimiters:
                    count = line.count(delim)
                    delimiters[delim] += count
            
            # Get delimiter with highest count
            best_delim = max(delimiters, key=delimiters.get)
            
            # If no delimiters found, default to comma
            if delimiters[best_delim] == 0:
                return ','
            
            # Additional validation: check if delimiter appears consistently
            # Count occurrences per line
            counts_per_line = []
            for line in lines:
                counts_per_line.append(line.count(best_delim))
            
            # If delimiter appears consistently (same count in most lines), it's likely correct
            if len(set(counts_per_line)) <= 2:  # Allow for header variation
                return best_delim
            
            # Otherwise, return the most common delimiter
            return best_delim
            
        except Exception as e:
            print(f"Error detecting delimiter: {e}")
            return ','  # Default to comma on error
    
    def _analyze_column(self, column_name: str, series: pd.Series) -> ColumnInfo:
        """Analyze a single column."""
        # Classify column type
        detected_type, confidence = self.classifier.classify_column(column_name, series)
        
        # Get sample values
        sample_values = series.dropna().head(5).tolist()
        
        # Calculate missing values
        missing_count = series.isna().sum()
        missing_percentage = (missing_count / len(series) * 100) if len(series) > 0 else 0
        
        # Get unique count
        unique_count = series.nunique()
        
        # Detect patterns
        patterns = self._detect_patterns(series)
        
        return ColumnInfo(
            name=str(column_name),
            detected_type=detected_type,
            confidence=confidence,
            sample_values=sample_values,
            missing_count=missing_count,
            missing_percentage=missing_percentage,
            unique_count=unique_count,
            data_type=str(series.dtype),
            patterns=patterns
        )
    
    def _detect_patterns(self, series: pd.Series) -> List[str]:
        """Detect common patterns in column data."""
        patterns = []
        sample = series.dropna().astype(str).head(20)
        
        if len(sample) == 0:
            return patterns
        
        # Check for time patterns
        for pattern_name, pattern in [
            ('HH:MM:SS', r'\d{1,2}:\d{2}:\d{2}'),
            ('MM:SS', r'\d{1,2}:\d{2}'),
            ('+SS.sss', r'\+\d+\.\d+'),
        ]:
            if any(re.search(pattern, str(val)) for val in sample):
                patterns.append(pattern_name)
        
        return patterns
    
    def _generate_mappings(self, columns_info: Dict[str, ColumnInfo]) -> Dict[str, str]:
        """Generate suggested column mappings to standard schema."""
        mappings = {}
        
        standard_schema = {
            ColumnType.POSITION: 'POSITION',
            ColumnType.LAP_NUMBER: 'LAPS',
            ColumnType.DRIVER_NAME: 'DRIVER',
            ColumnType.TEAM_NAME: 'TEAM',
            ColumnType.VEHICLE: 'VEHICLE',
            ColumnType.STATUS: 'STATUS',
        }
        
        # Additional direct name mappings
        name_mappings = {
            'LAP_TIME': 'FL_TIME',
            'KPH': 'FL_KPH',
            'GAP': 'GAP_FIRST',
            'DIFF': 'GAP_PREV',
            'LAP': 'LAPS',
            'DRIVER_NUMBER': 'DRIVER_IDX', # Avoid confusion with NUMBER
            'VEHICLE_NUMBER': 'NUMBER',
            'VEHICLE_ID': 'NUMBER',
        }
        
        used_targets = set()
        
        # First pass: Direct name mappings
        for col_name, col_info in columns_info.items():
            upper_name = col_name.upper().strip()
            if upper_name in name_mappings:
                target = name_mappings[upper_name]
                if target not in used_targets:
                    mappings[col_name] = target
                    used_targets.add(target)
        
        # Second pass: Type-based mappings
        for col_name, col_info in columns_info.items():
            if col_name in mappings:
                continue
                
            if col_info.detected_type in standard_schema and col_info.confidence > 0.7:
                target = standard_schema[col_info.detected_type]
                
                # Avoid duplicate targets
                if target not in used_targets:
                    mappings[col_name] = target
                    used_targets.add(target)
                else:
                    # Append suffix if target already used
                    # But actually, we should probably only map the best confidence one?
                    # For now, let's just skip duplicates to be safe
                    pass
        
        return mappings
    
    def _generate_warnings(self, columns_info: Dict[str, ColumnInfo], 
                          quality_metrics: Dict[str, Any]) -> List[str]:
        """Generate warnings about data quality issues."""
        warnings = []
        
        # Check for high missing percentages
        for col_name, col_info in columns_info.items():
            if col_info.missing_percentage > 50:
                warnings.append(f"Column '{col_name}' has {col_info.missing_percentage:.1f}% missing values")
        
        # Check for duplicate rows
        if quality_metrics['duplicate_rows'] > 0:
            warnings.append(f"Found {quality_metrics['duplicate_rows']} duplicate rows")
        
        # Check overall quality
        if quality_metrics['overall_quality_score'] < 50:
            warnings.append("Overall data quality is low - consider data cleaning")
        
        return warnings
