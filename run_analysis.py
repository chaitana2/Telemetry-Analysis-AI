#!/usr/bin/env python3
"""
Run Automated Telemetry Analysis

Usage:
    python run_analysis.py <input_file_or_directory> [--output <output_directory>]

Example:
    python run_analysis.py data/race_data.csv
    python run_analysis.py data/ --output reports/
"""

import sys
import os
import argparse

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from automated_analysis import AutomatedPipeline

def main():
    parser = argparse.ArgumentParser(description="Automated Telemetry Analysis Tool")
    parser.add_argument("input", help="Input CSV file or directory containing CSV files")
    parser.add_argument("--output", "-o", help="Output directory for generated reports", default=None)
    
    args = parser.parse_args()
    
    pipeline = AutomatedPipeline()
    
    if os.path.isdir(args.input):
        print(f"Processing directory: {args.input}")
        pipeline.process_directory(args.input, args.output)
    elif os.path.isfile(args.input):
        print(f"Processing file: {args.input}")
        pipeline.process_file(args.input, args.output)
    else:
        print(f"Error: Input path not found: {args.input}")
        sys.exit(1)

if __name__ == "__main__":
    main()
