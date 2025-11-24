import pandas as pd
import numpy as np
from typing import Optional

class DataLoader:
    """
    Handles loading and preprocessing of telemetry data from CSV files.

    Attributes:
        raw_data (Optional[pd.DataFrame]): The raw data loaded from the CSV.
        clean_data (Optional[pd.DataFrame]): The processed and cleaned data.
    """

    def __init__(self):
        """Initialize the DataLoader with empty data attributes."""
        self.raw_data: Optional[pd.DataFrame] = None
        self.clean_data: Optional[pd.DataFrame] = None

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
