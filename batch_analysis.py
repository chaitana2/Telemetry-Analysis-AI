#!/usr/bin/env python3
"""
Batch Analysis Script - Process multiple CSV files with progress tracking
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from automated_analysis import AutomatedPipeline

def main():
    # Configuration
    input_dir = "src/ml/data/raw"
    output_dir = "reports/batch_analysis"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize pipeline
    pipeline = AutomatedPipeline()
    
    # Find all CSV files
    csv_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    # Filter out very large telemetry files (>100MB) for now
    filtered_files = []
    large_files = []
    
    for f in csv_files:
        size_mb = os.path.getsize(f) / (1024 * 1024)
        if size_mb > 100:
            large_files.append((f, size_mb))
        else:
            filtered_files.append(f)
    
    print(f"Found {len(csv_files)} total CSV files")
    print(f"Processing {len(filtered_files)} files (skipping {len(large_files)} large telemetry files)")
    
    # Track results
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_files': len(csv_files),
        'processed_files': 0,
        'successful': [],
        'failed': [],
        'skipped_large': [{'file': f, 'size_mb': s} for f, s in large_files]
    }
    
    # Process each file
    for idx, file_path in enumerate(filtered_files, 1):
        print(f"\n{'='*80}")
        print(f"Processing {idx}/{len(filtered_files)}: {os.path.basename(file_path)}")
        print(f"{'='*80}")
        
        try:
            # Create output subdirectory
            rel_path = os.path.relpath(os.path.dirname(file_path), input_dir)
            current_output_dir = os.path.join(output_dir, rel_path)
            
            # Process file
            success = pipeline.process_file(file_path, current_output_dir)
            
            if success:
                results['successful'].append(file_path)
                results['processed_files'] += 1
            else:
                results['failed'].append({'file': file_path, 'reason': 'Processing returned False'})
                
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results['failed'].append({'file': file_path, 'reason': str(e)})
    
    # Save results summary
    summary_path = os.path.join(output_dir, 'batch_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\n{'='*80}")
    print("BATCH ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"Total files found: {results['total_files']}")
    print(f"Successfully processed: {len(results['successful'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Skipped (large files): {len(results['skipped_large'])}")
    print(f"\nSummary saved to: {summary_path}")
    print(f"Reports saved to: {output_dir}")
    
    if results['failed']:
        print("\nFailed files:")
        for item in results['failed']:
            print(f"  - {item['file']}: {item['reason']}")

if __name__ == "__main__":
    main()
