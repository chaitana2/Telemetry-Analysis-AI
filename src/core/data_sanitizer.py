"""
Data Sanitizer Module - AI-powered data cleaning and preprocessing.

This module provides intelligent data sanitization including missing value
imputation, outlier detection and correction, and data normalization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import IsolationForest
from dataclasses import dataclass



@dataclass
class SanitizationReport:
    """Report of sanitization operations performed."""
    rows_before: int
    rows_after: int
    columns_processed: int
    missing_values_imputed: int
    outliers_detected: int
    outliers_corrected: int
    duplicates_removed: int
    operations_performed: List[str]
    warnings: List[str]


class DataSanitizer:
    """
    Intelligent data cleaning and sanitization.
    """
    
    def __init__(self):
        """Initialize the sanitizer."""
        self.report = None
    
    def clean_data(self, df: pd.DataFrame, 
                   impute_missing: bool = True,
                   correct_outliers: bool = True,
                   remove_duplicates: bool = True,
                   normalize: bool = False) -> Tuple[pd.DataFrame, SanitizationReport]:
        """
        Perform comprehensive data cleaning.
        
        Args:
            df (pd.DataFrame): Input dataframe.
            impute_missing (bool): Whether to impute missing values.
            correct_outliers (bool): Whether to correct outliers.
            remove_duplicates (bool): Whether to remove duplicate rows.
            normalize (bool): Whether to normalize numeric columns.
        
        Returns:
            Tuple[pd.DataFrame, SanitizationReport]: Cleaned data and report.
        """
        operations = []
        warnings = []
        rows_before = len(df)
        df_clean = df.copy()
        
        # Ensure unique column names to prevent "truth value ambiguous" errors
        if not df_clean.columns.is_unique:
            warnings.append("Duplicate column names detected and renamed")
            # Simple deduplication: append .1, .2, etc.
            new_cols = []
            seen = {}
            for col in df_clean.columns:
                if col in seen:
                    seen[col] += 1
                    new_cols.append(f"{col}.{seen[col]}")
                else:
                    seen[col] = 0
                    new_cols.append(col)
            df_clean.columns = new_cols
        
        missing_imputed = 0
        outliers_detected = 0
        outliers_corrected = 0
        duplicates_removed = 0
        
        # Remove duplicates
        if remove_duplicates:
            duplicates_before = df_clean.duplicated().sum()
            if duplicates_before > 0:
                df_clean = df_clean.drop_duplicates()
                duplicates_removed = duplicates_before
                operations.append(f"Removed {duplicates_removed} duplicate rows")
        
        # Impute missing values
        if impute_missing:
            missing_before = df_clean.isna().sum().sum()
            if missing_before > 0:
                df_clean, imputed_count = self._impute_missing_values(df_clean)
                missing_imputed = imputed_count
                operations.append(f"Imputed {missing_imputed} missing values")
        
        # Correct outliers
        if correct_outliers:
            df_clean, outlier_stats = self._correct_outliers(df_clean)
            outliers_detected = outlier_stats['detected']
            outliers_corrected = outlier_stats['corrected']
            if outliers_detected > 0:
                operations.append(f"Detected {outliers_detected} outliers, corrected {outliers_corrected}")
        
        # Normalize data
        if normalize:
            df_clean = self._normalize_data(df_clean)
            operations.append("Normalized numeric columns")
        
        # Generate warnings
        if missing_imputed > len(df) * len(df.columns) * 0.3:
            warnings.append("High percentage of missing values imputed - results may be less reliable")
        
        if outliers_detected > len(df) * 0.2:
            warnings.append("High number of outliers detected - data may have quality issues")
        
        rows_after = len(df_clean)
        
        report = SanitizationReport(
            rows_before=rows_before,
            rows_after=rows_after,
            columns_processed=len(df_clean.columns),
            missing_values_imputed=missing_imputed,
            outliers_detected=outliers_detected,
            outliers_corrected=outliers_corrected,
            duplicates_removed=duplicates_removed,
            operations_performed=operations,
            warnings=warnings
        )
        
        self.report = report
        return df_clean, report
    
    def _impute_missing_values(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """
        Intelligently impute missing values.
        
        Args:
            df (pd.DataFrame): Input dataframe.
        
        Returns:
            Tuple[pd.DataFrame, int]: Cleaned dataframe and count of imputed values.
        """
        df_imputed = df.copy()
        imputed_count = 0
        
        for col in df_imputed.columns:
            missing_count = df_imputed[col].isna().sum()
            if missing_count == 0:
                continue
            
            # Numeric columns - use median or KNN
            if pd.api.types.is_numeric_dtype(df_imputed[col]):
                missing_ratio = missing_count / len(df_imputed)
                
                if missing_ratio < 0.3:
                    # Use median for low missing ratios
                    median_val = df_imputed[col].median()
                    df_imputed[col].fillna(median_val, inplace=True)
                else:
                    # Use forward fill for time series data
                    df_imputed[col].fillna(method='ffill', inplace=True)
                    df_imputed[col].fillna(method='bfill', inplace=True)
                
                imputed_count += missing_count
            
            # Categorical columns - use mode or forward fill
            else:
                # Try mode first
                if df_imputed[col].mode().shape[0] > 0:
                    mode_val = df_imputed[col].mode()[0]
                    df_imputed[col].fillna(mode_val, inplace=True)
                else:
                    # Use forward fill
                    df_imputed[col].fillna(method='ffill', inplace=True)
                    df_imputed[col].fillna(method='bfill', inplace=True)
                
                imputed_count += missing_count
        
        return df_imputed, imputed_count
    
    def _correct_outliers(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Detect and correct outliers using statistical methods.
        
        Args:
            df (pd.DataFrame): Input dataframe.
        
        Returns:
            Tuple[pd.DataFrame, Dict]: Cleaned dataframe and outlier statistics.
        """
        df_corrected = df.copy()
        total_detected = 0
        total_corrected = 0
        
        # Get numeric columns
        numeric_cols = df_corrected.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if df_corrected[col].isna().all():
                continue
            
            # Use IQR method for outlier detection
            Q1 = df_corrected[col].quantile(0.25)
            Q3 = df_corrected[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Detect outliers
            outliers = (df_corrected[col] < lower_bound) | (df_corrected[col] > upper_bound)
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                total_detected += outlier_count
                
                # Correct outliers by capping at bounds
                df_corrected.loc[df_corrected[col] < lower_bound, col] = lower_bound
                df_corrected.loc[df_corrected[col] > upper_bound, col] = upper_bound
                total_corrected += outlier_count
        
        return df_corrected, {'detected': total_detected, 'corrected': total_corrected}
    
    def _normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize numeric columns.
        
        Args:
            df (pd.DataFrame): Input dataframe.
        
        Returns:
            pd.DataFrame: Normalized dataframe.
        """
        df_normalized = df.copy()
        
        # Get numeric columns
        numeric_cols = df_normalized.select_dtypes(include=[np.number]).columns
        
        # Use StandardScaler for normalization
        scaler = StandardScaler()
        
        for col in numeric_cols:
            if df_normalized[col].isna().all():
                continue
            
            # Normalize
            values = df_normalized[col].values.reshape(-1, 1)
            df_normalized[col] = scaler.fit_transform(values)
        
        return df_normalized


class SmartImputer:
    """
    Advanced missing value imputation using machine learning.
    """
    
    def __init__(self, strategy: str = 'knn'):
        """
        Initialize the imputer.
        
        Args:
            strategy (str): Imputation strategy ('knn', 'iterative', 'simple').
        """
        self.strategy = strategy
        self.imputer = None
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit and transform data with imputation.
        
        Args:
            df (pd.DataFrame): Input dataframe.
        
        Returns:
            pd.DataFrame: Imputed dataframe.
        """
        # Separate numeric and non-numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
        
        df_imputed = df.copy()
        
        # Impute numeric columns
        if len(numeric_cols) > 0:
            if self.strategy == 'knn':
                self.imputer = KNNImputer(n_neighbors=5)
            else:
                self.imputer = SimpleImputer(strategy='median')
            
            df_imputed[numeric_cols] = self.imputer.fit_transform(df[numeric_cols])
        
        # Impute non-numeric columns with mode
        for col in non_numeric_cols:
            if df_imputed[col].isna().any():
                mode_val = df_imputed[col].mode()[0] if len(df_imputed[col].mode()) > 0 else 'Unknown'
                df_imputed[col].fillna(mode_val, inplace=True)
        
        return df_imputed


class OutlierDetector:
    """
    Advanced outlier detection using Isolation Forest.
    """
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize the detector.
        
        Args:
            contamination (float): Expected proportion of outliers.
        """
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
    
    def detect(self, df: pd.DataFrame) -> np.ndarray:
        """
        Detect outliers in dataframe.
        
        Args:
            df (pd.DataFrame): Input dataframe.
        
        Returns:
            np.ndarray: Boolean array indicating outliers.
        """
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return np.zeros(len(df), dtype=bool)
        
        # Prepare data
        X = df[numeric_cols].fillna(df[numeric_cols].median())
        
        # Detect outliers
        predictions = self.model.fit_predict(X)
        
        # -1 indicates outlier, 1 indicates inlier
        return predictions == -1
