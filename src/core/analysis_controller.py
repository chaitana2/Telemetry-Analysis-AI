"""
Analysis controller for coordinating data processing and AI analysis.

This module provides a central controller that manages the workflow
between data loading, AI model execution, and result formatting.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.models import AnomalyDetector, RaceCoach, LapTimePredictor


class AnalysisController:
    """
    Coordinates analysis workflows between data, AI models, and UI.
    
    Attributes:
        data (pd.DataFrame): The current telemetry dataset.
        anomaly_detector (AnomalyDetector): Anomaly detection model.
        race_coach (RaceCoach): Performance coaching model.
        lap_predictor (LapTimePredictor): Lap time prediction model.
        analysis_cache (dict): Cache for storing analysis results.
    """
    
    def __init__(self):
        """Initialize the analysis controller."""
        self.data: Optional[pd.DataFrame] = None
        self.anomaly_detector = AnomalyDetector(contamination=0.05)
        self.race_coach = RaceCoach()
        self.lap_predictor = LapTimePredictor()
        self.analysis_cache: Dict = {}
        
    def set_data(self, df: pd.DataFrame):
        """
        Set the current dataset for analysis.
        
        Args:
            df (pd.DataFrame): The telemetry dataframe.
        """
        self.data = df
        self.analysis_cache.clear()  # Clear cache when new data is loaded
        
    def load_data(self, df: pd.DataFrame):
        """Alias for set_data to maintain compatibility."""
        self.set_data(df)
        
    def run_anomaly_detection(self, features: List[str] = None) -> Dict:
        """
        Run anomaly detection on the current dataset.
        
        Args:
            features (List[str], optional): List of feature columns to use.
                Defaults to ['FL_TIME_SEC', 'FL_KPH', 'GAP_FIRST_SEC'].
        
        Returns:
            Dict: Results containing anomaly indices and statistics.
        """
        if self.data is None or self.data.empty:
            return {'error': 'No data available for analysis'}
        
        # Default features
        if features is None:
            features = ['FL_TIME_SEC', 'FL_KPH', 'GAP_FIRST_SEC']
        
        # Filter to available features
        available_features = [f for f in features if f in self.data.columns]
        
        if not available_features:
            return {'error': f'None of the requested features {features} are available'}
        
        # Prepare data
        feature_data = self.data[available_features].copy()
        feature_data = feature_data.dropna()
        
        if len(feature_data) < 2:
            return {'error': 'Insufficient data for anomaly detection (need at least 2 samples)'}
        
        # Train and predict
        try:
            self.anomaly_detector.train(feature_data.values)
            predictions = self.anomaly_detector.predict(feature_data.values)
            
            # Get anomaly indices (in original dataframe)
            anomaly_mask = predictions == -1
            anomaly_indices = feature_data.index[anomaly_mask].tolist()
            
            # Calculate statistics
            num_anomalies = len(anomaly_indices)
            total_samples = len(feature_data)
            anomaly_percentage = (num_anomalies / total_samples) * 100
            
            results = {
                'anomaly_indices': anomaly_indices,
                'num_anomalies': num_anomalies,
                'total_samples': total_samples,
                'anomaly_percentage': anomaly_percentage,
                'features_used': available_features,
                'success': True
            }
            
            # Cache results
            self.analysis_cache['anomaly_detection'] = results
            
            return results
            
        except Exception as e:
            return {'error': f'Anomaly detection failed: {str(e)}', 'success': False}
    
    def run_coaching_analysis(self, driver_number: int) -> Dict:
        """
        Generate coaching insights for a specific driver.
        
        Args:
            driver_number (int): The car number of the driver to analyze.
        
        Returns:
            Dict: Coaching insights and statistics.
        """
        if self.data is None or self.data.empty:
            return {'error': 'No data available for analysis'}
        
        if 'NUMBER' not in self.data.columns:
            return {'error': 'NUMBER column not found in data'}
        
        try:
            insights = self.race_coach.analyze_driver(self.data, driver_number)
            
            # Get driver name
            driver_data = self.data[self.data['NUMBER'] == driver_number]
            driver_name = driver_data['DRIVER'].iloc[0] if 'DRIVER' in driver_data.columns and not driver_data.empty else f"Car #{driver_number}"
            
            results = {
                'driver_number': driver_number,
                'driver_name': driver_name,
                'insights': insights,
                'num_data_points': len(driver_data),
                'success': True
            }
            
            # Cache results
            cache_key = f'coaching_{driver_number}'
            self.analysis_cache[cache_key] = results
            
            return results
            
        except Exception as e:
            return {'error': f'Coaching analysis failed: {str(e)}', 'success': False}
    
    def compare_drivers(self, driver_numbers: List[int]) -> Dict:
        """
        Compare performance metrics across multiple drivers.
        
        Args:
            driver_numbers (List[int]): List of driver car numbers to compare.
        
        Returns:
            Dict: Comparison statistics for each driver.
        """
        if self.data is None or self.data.empty:
            return {'error': 'No data available for analysis'}
        
        if 'NUMBER' not in self.data.columns:
            return {'error': 'NUMBER column not found in data'}
        
        try:
            comparison = {}
            
            for driver_num in driver_numbers:
                driver_data = self.data[self.data['NUMBER'] == driver_num]
                
                if driver_data.empty:
                    comparison[driver_num] = {'error': 'No data for this driver'}
                    continue
                
                # Calculate statistics
                stats = {}
                
                # Driver name
                stats['name'] = driver_data['DRIVER'].iloc[0] if 'DRIVER' in driver_data.columns else f"Car #{driver_num}"
                
                # Lap time statistics
                if 'FL_TIME_SEC' in driver_data.columns:
                    lap_times = driver_data['FL_TIME_SEC'].dropna()
                    if len(lap_times) > 0:
                        stats['avg_lap_time'] = lap_times.mean()
                        stats['best_lap_time'] = lap_times.min()
                        stats['worst_lap_time'] = lap_times.max()
                        stats['lap_time_std'] = lap_times.std()
                
                # Speed statistics
                if 'FL_KPH' in driver_data.columns:
                    speeds = driver_data['FL_KPH'].dropna()
                    if len(speeds) > 0:
                        stats['avg_speed'] = speeds.mean()
                        stats['max_speed'] = speeds.max()
                
                # Position statistics
                if 'POSITION' in driver_data.columns:
                    positions = driver_data['POSITION'].dropna()
                    if len(positions) > 0:
                        stats['avg_position'] = positions.mean()
                        stats['best_position'] = positions.min()
                
                comparison[driver_num] = stats
            
            results = {
                'comparison': comparison,
                'driver_numbers': driver_numbers,
                'success': True
            }
            
            return results
            
        except Exception as e:
            return {'error': f'Driver comparison failed: {str(e)}', 'success': False}
    
    def get_driver_list(self) -> List[Tuple[int, str]]:
        """
        Get list of available drivers in the dataset.
        
        Returns:
            List[Tuple[int, str]]: List of (driver_number, driver_name) tuples.
        """
        if self.data is None or self.data.empty:
            return []
        
        if 'NUMBER' not in self.data.columns:
            return []
        
        drivers = []
        for driver_num in self.data['NUMBER'].unique():
            if pd.notna(driver_num):
                driver_data = self.data[self.data['NUMBER'] == driver_num]
                driver_name = driver_data['DRIVER'].iloc[0] if 'DRIVER' in driver_data.columns and not driver_data.empty else f"Car #{int(driver_num)}"
                drivers.append((int(driver_num), driver_name))
        
        return sorted(drivers, key=lambda x: x[0])
    
    def get_summary_statistics(self) -> Dict:
        """
        Get summary statistics for the entire dataset.
        
        Returns:
            Dict: Summary statistics including counts, averages, etc.
        """
        if self.data is None or self.data.empty:
            return {'error': 'No data available'}
        
        stats = {
            'total_rows': len(self.data),
            'num_drivers': self.data['NUMBER'].nunique() if 'NUMBER' in self.data.columns else 0,
        }
        
        # Lap time statistics
        if 'FL_TIME_SEC' in self.data.columns:
            lap_times = self.data['FL_TIME_SEC'].dropna()
            if len(lap_times) > 0:
                stats['overall_avg_lap_time'] = lap_times.mean()
                stats['overall_best_lap_time'] = lap_times.min()
                stats['overall_worst_lap_time'] = lap_times.max()
        
        # Speed statistics
        if 'FL_KPH' in self.data.columns:
            speeds = self.data['FL_KPH'].dropna()
            if len(speeds) > 0:
                stats['overall_avg_speed'] = speeds.mean()
                stats['overall_max_speed'] = speeds.max()
        
        return stats
