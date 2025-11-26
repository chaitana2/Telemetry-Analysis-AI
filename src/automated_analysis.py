"""
Automated Analysis Pipeline

This module provides a high-level interface for running the entire
analysis pipeline: data loading, conversion, analysis, and reporting.
"""

import os
import sys
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.data_loader import DataLoader
from src.core.analysis_controller import AnalysisController
from src.core.export import PDFReporter

class AutomatedPipeline:
    """
    Orchestrates the automated analysis workflow.
    """
    
    def __init__(self):
        """Initialize the pipeline components."""
        self.loader = DataLoader()
        self.controller = AnalysisController()
        self.reporter = PDFReporter()
        
    def process_file(self, input_path: str, output_dir: str = None) -> bool:
        """
        Process a single telemetry file.
        
        Args:
            input_path (str): Path to the input CSV file.
            output_dir (str, optional): Directory to save the report. 
                                      Defaults to same directory as input.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not os.path.exists(input_path):
            print(f"Error: Input file not found: {input_path}")
            return False
            
        print(f"Starting analysis for: {input_path}")
        
        # 1. Auto Data Conversion
        print("Step 1: Auto Data Conversion...")
        df = self.loader.smart_load(input_path)
        
        if df is None or df.empty:
            print("Error: Failed to load or convert data.")
            return False
            
        # 2. Automated Analysis
        print("Step 2: Automated Analysis...")
        self.controller.set_data(df)
        
        # Run all available analyses
        summary_stats = self.controller.get_summary_statistics()
        anomaly_results = self.controller.run_anomaly_detection()
        
        # Run coaching for all drivers
        analysis_results = {'anomaly_detection': anomaly_results}
        
        drivers = self.controller.get_driver_list()
        print(f"Analyzing {len(drivers)} drivers...")
        
        for driver_num, driver_name in drivers:
            print(f"  - Analyzing driver: {driver_name} (#{driver_num})")
            coaching = self.controller.run_coaching_analysis(driver_num)
            analysis_results[f'coaching_{driver_num}'] = coaching
            
        # 3. Automated Report Generation
        print("Step 3: Automated Report Generation...")
        
        if output_dir is None:
            output_dir = os.path.dirname(input_path)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = os.path.basename(input_path)
        report_name = f"Report_{os.path.splitext(filename)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        report_path = os.path.join(output_dir, report_name)
        
        success = self.reporter.generate_report(
            report_path, 
            df, 
            analysis_results, 
            summary_stats
        )
        
        if success:
            print(f"Analysis complete! Report saved to: {report_path}")
        else:
            print("Error: Failed to generate report.")
            
        return success

    def process_directory(self, input_dir: str, output_dir: str = None) -> None:
        """
        Process all CSV files in a directory recursively.
        
        Args:
            input_dir (str): Directory containing CSV files.
            output_dir (str, optional): Directory to save reports.
        """
        if not os.path.exists(input_dir):
            print(f"Error: Directory not found: {input_dir}")
            return
            
        csv_files = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.csv'):
                    csv_files.append(os.path.join(root, file))
        
        if not csv_files:
            print(f"No CSV files found in {input_dir}")
            return
            
        print(f"Found {len(csv_files)} CSV files to process.")
        
        for file_path in csv_files:
            # Create a corresponding output subdirectory structure if output_dir is specified
            current_output_dir = output_dir
            if output_dir:
                rel_path = os.path.relpath(os.path.dirname(file_path), input_dir)
                current_output_dir = os.path.join(output_dir, rel_path)
                
            self.process_file(file_path, current_output_dir)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Telemetry Analysis Pipeline")
    parser.add_argument("input", help="Input file or directory path")
    parser.add_argument("--output", "-o", help="Output directory for reports", default=None)
    
    args = parser.parse_args()
    
    pipeline = AutomatedPipeline()
    
    if os.path.isdir(args.input):
        pipeline.process_directory(args.input, args.output)
    else:
        pipeline.process_file(args.input, args.output)
