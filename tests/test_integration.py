"""
Integration tests for the Telemetry Analysis Tool.

This module contains end-to-end tests that verify the complete workflow
from data loading through AI analysis.
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.data_loader import DataLoader
from src.ai.models import AnomalyDetector, RaceCoach


class TestEndToEndWorkflow:
    """Test complete data processing workflow."""
    
    def test_load_and_analyze_workflow(self, tmp_path):
        """
        Test the complete workflow: load CSV -> preprocess -> analyze.
        
        This integration test verifies that:
        1. CSV data loads correctly
        2. Preprocessing converts time formats
        3. AI models can consume the processed data
        4. Coach generates insights
        """
        # Arrange: Create test CSV
        csv_content = """POSITION,NUMBER,DRIVER,TEAM,VEHICLE,LAPS,TOTAL_TIME,GAP_FIRST,FL_TIME,FL_KPH,STATUS
1,14,Jack Hawksworth,Vasser Sullivan,Lexus RC F GT3,50,1:30:45.123,,1:35.678,160.5,Running
2,3,Jan Heylen,Wright Motorsports,Porsche 911 GT3 R,50,1:30:50.456,+5.333,1:36.123,159.8,Running
3,93,Racers Edge,Racers Edge,Acura NSX GT3,49,1:31:00.000,+1:14.985,1:37.000,158.0,Running
4,14,Jack Hawksworth,Vasser Sullivan,Lexus RC F GT3,51,1:32:20.801,,1:35.500,160.7,Running
5,3,Jan Heylen,Wright Motorsports,Porsche 911 GT3 R,51,1:32:26.579,+5.778,1:36.000,159.9,Running
"""
        csv_file = tmp_path / "telemetry.csv"
        csv_file.write_text(csv_content)
        
        # Act: Load and process
        loader = DataLoader()
        assert loader.load_csv(str(csv_file)) is True
        df = loader.preprocess()
        
        # Assert: Data structure
        assert df is not None
        assert len(df) == 5
        assert 'TOTAL_TIME_SEC' in df.columns
        assert 'FL_TIME_SEC' in df.columns
        
        # Assert: Time conversions
        assert df.iloc[0]['TOTAL_TIME_SEC'] == pytest.approx(5445.123, rel=1e-3)
        assert df.iloc[1]['GAP_FIRST_SEC'] == pytest.approx(5.333, rel=1e-3)
        assert df.iloc[2]['GAP_FIRST_SEC'] == pytest.approx(74.985, rel=1e-3)
        
        # Act: Generate coaching insights
        coach = RaceCoach()
        insights = coach.analyze_driver(df, 14)
        
        # Assert: Insights generated
        assert len(insights) > 0
        assert any("Average Lap Time" in insight for insight in insights)
        assert any("Consistency" in insight for insight in insights)


class TestAnomalyDetection:
    """Test anomaly detection on realistic data."""
    
    def test_detect_outliers_in_lap_times(self):
        """
        Test that anomaly detector identifies unusual lap times.
        
        Creates a dataset with mostly consistent lap times and one outlier.
        """
        # Arrange: Create synthetic data with outlier
        normal_laps = np.random.normal(95.0, 0.5, 50)  # Mean 95s, std 0.5s
        outlier_lap = np.array([110.0])  # Significantly slower
        all_laps = np.concatenate([normal_laps, outlier_lap])
        
        # Reshape for model (needs 2D array)
        data = all_laps.reshape(-1, 1)
        
        # Act: Train and predict
        detector = AnomalyDetector(contamination=0.05)
        detector.train(data)
        predictions = detector.predict(data)
        
        # Assert: Outlier detected
        assert predictions[-1] == -1  # Last value (outlier) should be flagged
        assert np.sum(predictions == -1) >= 1  # At least one outlier


class TestDataQuality:
    """Test data quality and edge cases."""
    
    def test_handle_missing_values(self, tmp_path):
        """Test that missing values are handled gracefully."""
        csv_content = """POSITION,NUMBER,TOTAL_TIME,FL_TIME
1,14,1:30:45.123,
2,3,,1:36.123
3,93,1:31:00.000,1:37.000
"""
        csv_file = tmp_path / "missing.csv"
        csv_file.write_text(csv_content)
        
        loader = DataLoader()
        loader.load_csv(str(csv_file))
        df = loader.preprocess()
        
        # Assert: NaN values preserved
        assert pd.isna(df.iloc[0]['FL_TIME_SEC'])
        assert pd.isna(df.iloc[1]['TOTAL_TIME_SEC'])
        assert not pd.isna(df.iloc[2]['TOTAL_TIME_SEC'])
    
    def test_handle_malformed_time_strings(self):
        """Test parsing of edge case time formats."""
        loader = DataLoader()
        
        # Valid formats
        assert loader.parse_time_str("1:30:45.123") == pytest.approx(5445.123)
        assert loader.parse_time_str("1:35.678") == pytest.approx(95.678)
        assert loader.parse_time_str("+5.234") == pytest.approx(5.234)
        
        # Invalid formats should return NaN
        assert np.isnan(loader.parse_time_str("invalid"))
        assert np.isnan(loader.parse_time_str(""))
        assert np.isnan(loader.parse_time_str("1:2:3:4"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
