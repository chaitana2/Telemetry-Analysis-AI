import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import sys
import os

# Import CSV intelligence modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
try:
    from csv_intelligence import CSVSchemaAnalyzer, SchemaAnalysis
    from data_sanitizer import DataSanitizer
    from data_transformer import DataTransformer
except ImportError:
    CSVSchemaAnalyzer = None
    DataSanitizer = None
    DataTransformer = None

class DataLoader:
    """
    Handles loading and preprocessing of telemetry data from CSV files.

    Attributes:
        raw_data (Optional[pd.DataFrame]): The raw data loaded from the CSV.
        clean_data (Optional[pd.DataFrame]): The processed and cleaned data.
        schema_analysis (Optional[SchemaAnalysis]): Schema analysis results.
    """

    def __init__(self):
        """Initialize the DataLoader with empty data attributes."""
        self.raw_data: Optional[pd.DataFrame] = None
        self.clean_data: Optional[pd.DataFrame] = None
        self.schema_analysis: Optional[SchemaAnalysis] = None
        
        # Initialize intelligent modules if available
        self.schema_analyzer = CSVSchemaAnalyzer() if CSVSchemaAnalyzer else None
        self.sanitizer = DataSanitizer() if DataSanitizer else None
        self.transformer = DataTransformer() if DataTransformer else None

    def load_csv(self, filepath: str) -> bool:
        """
        Loads telemetry data from a CSV file.

        Args:
            filepath (str): The absolute path to the CSV file.

        Returns:
            bool: True if loading was successful, False otherwise.
        """
        try:
            self.raw_data = pd.read_csv(filepath)
            print(f"Successfully loaded {len(self.raw_data)} rows from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
    def smart_load(self, filepath: str, auto_clean: bool = True, 
                   auto_transform: bool = True) -> Optional[pd.DataFrame]:
        """
        Intelligently load CSV with automatic schema detection and cleaning.
        
        Args:
            filepath (str): Path to CSV file.
            auto_clean (bool): Automatically clean data.
            auto_transform (bool): Automatically transform data.
        
        Returns:
            Optional[pd.DataFrame]: Loaded and processed dataframe.
        """
        if not self.schema_analyzer:
            # Fallback to regular load
            if self.load_csv(filepath):
                return self.preprocess()
            return None
        
        try:
            # Analyze schema first
            print("Analyzing CSV schema...")
            self.schema_analysis = self.schema_analyzer.analyze_file(filepath)
            
            print(f"Detected {self.schema_analysis.total_columns} columns")
            print(f"Data quality score: {self.schema_analysis.overall_quality_score:.1f}%")
            
            # Load with detected parameters
            self.raw_data = pd.read_csv(
                filepath,
                encoding=self.schema_analysis.encoding,
                delimiter=self.schema_analysis.delimiter
            )
            
            # Apply suggested mappings
            if self.schema_analysis.suggested_mappings:
                print(f"Applying {len(self.schema_analysis.suggested_mappings)} column mappings")
                self.raw_data.rename(columns=self.schema_analysis.suggested_mappings, inplace=True)
            
            # Check for long-format telemetry data and pivot if necessary
            if self.transformer:
                self.raw_data = self.transformer.pivot_telemetry_data(self.raw_data)
            
            # Auto-clean if requested
            if auto_clean and self.sanitizer:
                print("Cleaning data...")
                self.raw_data, sanitization_report = self.sanitizer.clean_data(
                    self.raw_data,
                    impute_missing=True,
                    correct_outliers=True,
                    remove_duplicates=True
                )
                print(f"Sanitization: {', '.join(sanitization_report.operations_performed)}")
            
            # Preprocess
            self.clean_data = self.preprocess()
            
            # Auto-transform if requested
            if auto_transform and self.transformer and self.clean_data is not None:
                print("Generating derived features...")
                self.clean_data = self.transformer.generate_derived_features(self.clean_data)
            
            # Display warnings
            if self.schema_analysis.warnings:
                print("\nWarnings:")
                for warning in self.schema_analysis.warnings:
                    print(f"  ⚠ {warning}")
            
            return self.clean_data
            
        except Exception as e:
            print(f"Error in smart load: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to regular load, but try to use detected delimiter if available
            delimiter = ','
            if self.schema_analysis and self.schema_analysis.delimiter:
                delimiter = self.schema_analysis.delimiter
                
            try:
                self.raw_data = pd.read_csv(filepath, delimiter=delimiter)
                print(f"Fallback loaded {len(self.raw_data)} rows with delimiter '{delimiter}'")
                return self.preprocess()
            except Exception as e2:
                print(f"Fallback failed: {e2}")
                # Last resort: default read_csv
                if self.load_csv(filepath):
                    return self.preprocess()
                return None
    
    def get_schema_info(self) -> Optional[Dict[str, Any]]:
        """
        Get schema analysis information.
        
        Returns:
            Optional[Dict[str, Any]]: Schema information.
        """
        if not self.schema_analysis:
            return None
        
        return {
            'total_columns': self.schema_analysis.total_columns,
            'total_rows': self.schema_analysis.total_rows,
            'quality_score': self.schema_analysis.overall_quality_score,
            'encoding': self.schema_analysis.encoding,
            'delimiter': self.schema_analysis.delimiter,
            'columns': {
                name: {
                    'type': info.detected_type.value,
                    'confidence': info.confidence,
                    'missing_percentage': info.missing_percentage
                }
                for name, info in self.schema_analysis.columns.items()
            },
            'warnings': self.schema_analysis.warnings
        }

    def parse_time_str(self, time_str: str) -> float:
        """
        Converts time strings (MM:SS.sss or +SS.sss) to seconds.

        Args:
            time_str (str): The time string to parse.

        Returns:
            float: The time in seconds, or np.nan if parsing fails.
        """
        if pd.isna(time_str) or time_str == '':
            return np.nan
        
        time_str = str(time_str).strip()
        
        # Handle "Gap" format like "+1:14.985" or "+5.234"
        if time_str.startswith('+'):
            time_str = time_str[1:]
            
        try:
            parts = time_str.split(':')
            if len(parts) == 3: # HH:MM:SS.sss
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2: # MM:SS.sss
                minutes = float(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            elif len(parts) == 1: # SS.sss
                return float(parts[0])
            else:
                return np.nan
        except ValueError:
            return np.nan

    def preprocess(self) -> Optional[pd.DataFrame]:
        """
        Cleans and preprocesses the loaded data.

        Standardizes column names, converts time columns to seconds,
        and ensures numeric types for key metrics.

        Returns:
            Optional[pd.DataFrame]: The cleaned dataframe, or None if no data is loaded.
        """
        if self.raw_data is None:
            print("No data loaded.")
            return None

        df = self.raw_data.copy()

        # Standardize column names (strip whitespace, upper case)
        df.columns = [c.strip().upper() for c in df.columns]

        # Convert Time Columns
        time_cols = ['TOTAL_TIME', 'GAP_FIRST', 'FL_TIME', 'DIFF_PREV']
        for col in time_cols:
            if col in df.columns:
                df[f'{col}_SEC'] = df[col].apply(self.parse_time_str)

        # Convert Numeric Columns
        numeric_cols = ['POSITION', 'NUMBER', 'LAPS', 'FL_KPH']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Categorical Encoding (Example: STATUS)
        if 'STATUS' in df.columns:
            df['STATUS'] = df['STATUS'].astype(str)

        self.clean_data = df
        return self.clean_data

