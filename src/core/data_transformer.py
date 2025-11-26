"""
Data Transformer - Intelligent data transformation and feature engineering.

This module provides automatic unit detection and conversion, feature
engineering, and intelligent data transformation capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass


@dataclass
class UnitInfo:
    """Information about detected units."""
    column: str
    detected_unit: str
    confidence: float
    conversion_available: bool


class UnitConverter:
    """
    Handles unit detection and conversion.
    """
    
    # Unit conversion factors
    SPEED_CONVERSIONS = {
        ('km/h', 'mph'): 0.621371,
        ('mph', 'km/h'): 1.60934,
        ('km/h', 'm/s'): 0.277778,
        ('m/s', 'km/h'): 3.6,
        ('mph', 'm/s'): 0.44704,
        ('m/s', 'mph'): 2.23694,
    }
    
    DISTANCE_CONVERSIONS = {
        ('km', 'miles'): 0.621371,
        ('miles', 'km'): 1.60934,
        ('km', 'm'): 1000,
        ('m', 'km'): 0.001,
        ('miles', 'm'): 1609.34,
        ('m', 'miles'): 0.000621371,
    }
    
    TEMPERATURE_CONVERSIONS = {
        ('C', 'F'): lambda x: x * 9/5 + 32,
        ('F', 'C'): lambda x: (x - 32) * 5/9,
        ('C', 'K'): lambda x: x + 273.15,
        ('K', 'C'): lambda x: x - 273.15,
        ('F', 'K'): lambda x: (x - 32) * 5/9 + 273.15,
        ('K', 'F'): lambda x: (x - 273.15) * 9/5 + 32,
    }
    
    def __init__(self):
        """Initialize the converter."""
        pass
    
    def detect_unit(self, column_name: str, series: pd.Series) -> UnitInfo:
        """
        Detect the unit of measurement in a column.
        
        Args:
            column_name (str): Column name.
            series (pd.Series): Column data.
        
        Returns:
            UnitInfo: Detected unit information.
        """
        col_lower = column_name.lower()
        
        # Speed units
        if any(keyword in col_lower for keyword in ['speed', 'velocity']):
            if 'kph' in col_lower or 'km/h' in col_lower or 'kmh' in col_lower:
                return UnitInfo(column_name, 'km/h', 0.95, True)
            elif 'mph' in col_lower:
                return UnitInfo(column_name, 'mph', 0.95, True)
            elif 'm/s' in col_lower or 'ms' in col_lower:
                return UnitInfo(column_name, 'm/s', 0.90, True)
            else:
                # Infer from data range
                median_val = series.median()
                if 0 < median_val < 50:
                    return UnitInfo(column_name, 'm/s', 0.6, True)
                elif 50 < median_val < 200:
                    return UnitInfo(column_name, 'km/h', 0.7, True)
                else:
                    return UnitInfo(column_name, 'unknown', 0.3, False)
        
        # Distance units
        if any(keyword in col_lower for keyword in ['distance', 'dist']):
            if 'km' in col_lower:
                return UnitInfo(column_name, 'km', 0.95, True)
            elif 'mile' in col_lower:
                return UnitInfo(column_name, 'miles', 0.95, True)
            elif 'm' in col_lower or 'meter' in col_lower:
                return UnitInfo(column_name, 'm', 0.90, True)
            else:
                return UnitInfo(column_name, 'unknown', 0.3, False)
        
        # Temperature units
        if any(keyword in col_lower for keyword in ['temp', 'temperature']):
            if 'c' in col_lower or 'celsius' in col_lower:
                return UnitInfo(column_name, 'C', 0.95, True)
            elif 'f' in col_lower or 'fahrenheit' in col_lower:
                return UnitInfo(column_name, 'F', 0.95, True)
            elif 'k' in col_lower or 'kelvin' in col_lower:
                return UnitInfo(column_name, 'K', 0.90, True)
            else:
                # Infer from data range
                median_val = series.median()
                if 200 < median_val < 400:
                    return UnitInfo(column_name, 'K', 0.6, True)
                elif -50 < median_val < 150:
                    return UnitInfo(column_name, 'C', 0.7, True)
                else:
                    return UnitInfo(column_name, 'unknown', 0.3, False)
        
        return UnitInfo(column_name, 'unknown', 0.0, False)
    
    def convert_speed(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert speed between units."""
        key = (from_unit, to_unit)
        if key in self.SPEED_CONVERSIONS:
            return value * self.SPEED_CONVERSIONS[key]
        return value
    
    def convert_distance(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert distance between units."""
        key = (from_unit, to_unit)
        if key in self.DISTANCE_CONVERSIONS:
            return value * self.DISTANCE_CONVERSIONS[key]
        return value
    
    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert temperature between units."""
        key = (from_unit, to_unit)
        if key in self.TEMPERATURE_CONVERSIONS:
            converter = self.TEMPERATURE_CONVERSIONS[key]
            if callable(converter):
                return converter(value)
            return value * converter
        return value


class DataTransformer:
    """
    Intelligent data transformation and feature engineering.
    """
    
    def __init__(self):
        """Initialize the transformer."""
        self.unit_converter = UnitConverter()
    
    def detect_and_convert_units(self, df: pd.DataFrame, 
                                 target_units: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Detect units and convert to target units.
        
        Args:
            df (pd.DataFrame): Input dataframe.
            target_units (Optional[Dict[str, str]]): Target units for conversion.
                Example: {'speed': 'mph', 'distance': 'miles'}
        
        Returns:
            pd.DataFrame: Dataframe with converted units.
        """
        df_converted = df.copy()
        
        if target_units is None:
            target_units = {'speed': 'km/h', 'distance': 'km', 'temperature': 'C'}
        
        for col in df_converted.columns:
            if not pd.api.types.is_numeric_dtype(df_converted[col]):
                continue
            
            # Detect unit
            unit_info = self.unit_converter.detect_unit(col, df_converted[col])
            
            if not unit_info.conversion_available:
                continue
            
            # Determine target unit
            target_unit = None
            if 'speed' in col.lower() and 'speed' in target_units:
                target_unit = target_units['speed']
            elif 'distance' in col.lower() and 'distance' in target_units:
                target_unit = target_units['distance']
            elif 'temp' in col.lower() and 'temperature' in target_units:
                target_unit = target_units['temperature']
            
            if target_unit and target_unit != unit_info.detected_unit:
                # Perform conversion
                if 'speed' in col.lower():
                    df_converted[col] = df_converted[col].apply(
                        lambda x: self.unit_converter.convert_speed(x, unit_info.detected_unit, target_unit)
                        if pd.notna(x) else x
                    )
                    # Update column name
                    new_col_name = col.replace(unit_info.detected_unit, target_unit)
                    df_converted.rename(columns={col: new_col_name}, inplace=True)
        
        return df_converted
    
    def generate_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate derived features from existing data.
        
        Args:
            df (pd.DataFrame): Input dataframe.
        
        Returns:
            pd.DataFrame: Dataframe with derived features.
        """
        df_derived = df.copy()
        
        # Lap time delta (if lap time column exists)
        lap_time_cols = [col for col in df_derived.columns if 'lap' in col.lower() and 'time' in col.lower()]
        for col in lap_time_cols:
            if pd.api.types.is_numeric_dtype(df_derived[col]):
                df_derived[f'{col}_DELTA'] = df_derived[col].diff()
                df_derived[f'{col}_ROLLING_AVG'] = df_derived[col].rolling(window=3, min_periods=1).mean()
        
        # Speed delta
        speed_cols = [col for col in df_derived.columns if 'speed' in col.lower()]
        for col in speed_cols:
            if pd.api.types.is_numeric_dtype(df_derived[col]):
                df_derived[f'{col}_DELTA'] = df_derived[col].diff()
        
        # Position changes
        if 'POSITION' in df_derived.columns:
            df_derived['POSITION_CHANGE'] = -df_derived['POSITION'].diff()  # Negative because lower position is better
            df_derived['POSITION_GAINED'] = df_derived['POSITION_CHANGE'].apply(lambda x: max(0, x) if pd.notna(x) else 0)
            df_derived['POSITION_LOST'] = df_derived['POSITION_CHANGE'].apply(lambda x: max(0, -x) if pd.notna(x) else 0)
        
        # Gap analysis
        gap_cols = [col for col in df_derived.columns if 'gap' in col.lower()]
        for col in gap_cols:
            if pd.api.types.is_numeric_dtype(df_derived[col]):
                df_derived[f'{col}_TREND'] = df_derived[col].diff()  # Positive = gap increasing
        
        return df_derived
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform advanced feature engineering.
        
        Args:
            df (pd.DataFrame): Input dataframe.
        
        Returns:
            pd.DataFrame: Dataframe with engineered features.
        """
        df_engineered = df.copy()
        
        # Rolling statistics for numeric columns
        numeric_cols = df_engineered.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Skip if column has too many missing values
            if df_engineered[col].isna().sum() > len(df_engineered) * 0.5:
                continue
            
            # Rolling mean (3-period window)
            df_engineered[f'{col}_MA3'] = df_engineered[col].rolling(window=3, min_periods=1).mean()
            
            # Rolling standard deviation
            df_engineered[f'{col}_STD3'] = df_engineered[col].rolling(window=3, min_periods=1).std()
            
            # Cumulative sum
            df_engineered[f'{col}_CUMSUM'] = df_engineered[col].cumsum()
        
        # Interaction features (if driver and lap time exist)
        if 'DRIVER' in df_engineered.columns:
            for col in numeric_cols:
                if 'time' in col.lower():
                    # Driver average lap time
                    driver_avg = df_engineered.groupby('DRIVER')[col].transform('mean')
                    df_engineered[f'{col}_VS_DRIVER_AVG'] = df_engineered[col] - driver_avg
        
        return df_engineered
    
    def create_time_features(self, df: pd.DataFrame, time_column: str) -> pd.DataFrame:
        """
        Create time-based features from a datetime column.
        
        Args:
            df (pd.DataFrame): Input dataframe.
            time_column (str): Name of the time column.
        
        Returns:
            pd.DataFrame: Dataframe with time features.
        """
        df_time = df.copy()
        
        if time_column not in df_time.columns:
            return df_time
        
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df_time[time_column]):
            try:
                df_time[time_column] = pd.to_datetime(df_time[time_column])
            except:
                return df_time
        
        # Extract time features
        df_time[f'{time_column}_HOUR'] = df_time[time_column].dt.hour
        df_time[f'{time_column}_MINUTE'] = df_time[time_column].dt.minute
        df_time[f'{time_column}_SECOND'] = df_time[time_column].dt.second
        df_time[f'{time_column}_DAY_OF_WEEK'] = df_time[time_column].dt.dayofweek
        df_time[f'{time_column}_IS_WEEKEND'] = df_time[time_column].dt.dayofweek.isin([5, 6]).astype(int)
        
        return df_time
    
    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names to standard format.
        
        Args:
            df (pd.DataFrame): Input dataframe.
        
        Returns:
            pd.DataFrame: Dataframe with normalized column names.
        """
        df_normalized = df.copy()
        
        # Convert to uppercase and replace spaces with underscores
        new_columns = {}
        for col in df_normalized.columns:
            new_col = str(col).strip().upper().replace(' ', '_')
            new_col = re.sub(r'[^\w\s]', '', new_col)  # Remove special characters
            new_columns[col] = new_col
        
        df_normalized.rename(columns=new_columns, inplace=True)
        
        return df_normalized

    def pivot_telemetry_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pivot long-format telemetry data to wide format.
        
        Args:
            df (pd.DataFrame): Input dataframe in long format.
            
        Returns:
            pd.DataFrame: Pivoted dataframe in wide format.
        """
        # Check if necessary columns exist
        required_cols = ['telemetry_name', 'telemetry_value']
        # Case insensitive check
        df_cols_lower = [c.lower() for c in df.columns]
        
        if not all(col in df_cols_lower for col in required_cols):
            return df
            
        print("Detected long-format telemetry data. Pivoting...")
        
        # Map actual column names
        col_map = {c.lower(): c for c in df.columns}
        name_col = col_map['telemetry_name']
        val_col = col_map['telemetry_value']
        
        # Identify index columns (everything else)
        index_cols = [c for c in df.columns if c.lower() not in required_cols]
        
        # We need a unique index for pivoting. 
        # Usually timestamp + vehicle + lap is good, but timestamp might be duplicated for different sensors.
        # So we group by timestamp/vehicle and pivot.
        
        # Find potential index columns like timestamp, vehicle_id, lap
        potential_indices = []
        for key in ['timestamp', 'time', 'meta_time', 'vehicle_id', 'vehicle_number', 'lap', 'outing']:
            for col in df.columns:
                if key in col.lower():
                    potential_indices.append(col)
        
        potential_indices = list(set(potential_indices))
        
        if not potential_indices:
            print("Warning: Could not identify index columns for pivoting.")
            return df
            
        try:
            # Pivot the table
            # We use pivot_table with 'first' aggregation to handle duplicates if any
            df_pivoted = df.pivot_table(
                index=potential_indices,
                columns=name_col,
                values=val_col,
                aggfunc='first'
            ).reset_index()
            
            print(f"Pivoted data: {len(df_pivoted)} rows, {len(df_pivoted.columns)} columns")
            return df_pivoted
            
        except Exception as e:
            print(f"Error pivoting data: {e}")
            return df
