"""
Export functionality for telemetry data and analysis results.

This module provides CSV and PDF export capabilities for processed
telemetry data and analysis reports.
"""

import pandas as pd
from typing import Dict, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os


class CSVExporter:
    """
    Exports processed telemetry data to CSV format.
    
    Handles exporting dataframes with optional filtering and formatting.
    """
    
    @staticmethod
    def export(df: pd.DataFrame, filepath: str, include_index: bool = False) -> bool:
        """
        Export dataframe to CSV file.
        
        Args:
            df (pd.DataFrame): The dataframe to export.
            filepath (str): The output file path.
            include_index (bool): Whether to include the index column.
        
        Returns:
            bool: True if export was successful, False otherwise.
        """
        try:
            df.to_csv(filepath, index=include_index)
            print(f"Successfully exported data to {filepath}")
            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False


class PDFReporter:
    """
    Generates PDF reports with telemetry analysis results.
    
    Creates formatted PDF documents with summary statistics,
    tables, and analysis insights.
    """
    
    def __init__(self):
        """Initialize the PDF reporter."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Insight style
        self.styles.add(ParagraphStyle(
            name='Insight',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=6
        ))
    
    def generate_report(self, filepath: str, data: pd.DataFrame, 
                       analysis_results: Dict, summary_stats: Dict) -> bool:
        """
        Generate a comprehensive PDF report.
        
        Args:
            filepath (str): Output PDF file path.
            data (pd.DataFrame): The telemetry dataframe.
            analysis_results (Dict): Results from analysis controller.
            summary_stats (Dict): Summary statistics.
        
        Returns:
            bool: True if report generation was successful, False otherwise.
        """
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Title
            title = Paragraph("Telemetry Analysis Report", self.styles['CustomTitle'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Timestamp
            timestamp = Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                self.styles['Normal']
            )
            elements.append(timestamp)
            elements.append(Spacer(1, 20))
            
            # Summary Statistics Section
            elements.append(Paragraph("Summary Statistics", self.styles['SectionHeader']))
            elements.append(Spacer(1, 12))
            
            if summary_stats and 'error' not in summary_stats:
                summary_data = [
                    ['Metric', 'Value'],
                    ['Total Data Points', str(summary_stats.get('total_rows', 'N/A'))],
                    ['Number of Drivers', str(summary_stats.get('num_drivers', 'N/A'))],
                ]
                
                if 'overall_avg_lap_time' in summary_stats:
                    summary_data.append(['Average Lap Time', f"{summary_stats['overall_avg_lap_time']:.2f}s"])
                if 'overall_best_lap_time' in summary_stats:
                    summary_data.append(['Best Lap Time', f"{summary_stats['overall_best_lap_time']:.2f}s"])
                if 'overall_avg_speed' in summary_stats:
                    summary_data.append(['Average Speed', f"{summary_stats['overall_avg_speed']:.1f} km/h"])
                if 'overall_max_speed' in summary_stats:
                    summary_data.append(['Maximum Speed', f"{summary_stats['overall_max_speed']:.1f} km/h"])
                
                summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 20))
            
            # Anomaly Detection Results
            if 'anomaly_detection' in analysis_results:
                anomaly_results = analysis_results['anomaly_detection']
                if anomaly_results.get('success'):
                    elements.append(Paragraph("Anomaly Detection Results", self.styles['SectionHeader']))
                    elements.append(Spacer(1, 12))
                    
                    anomaly_text = f"""
                    <b>Total Samples Analyzed:</b> {anomaly_results['total_samples']}<br/>
                    <b>Anomalies Detected:</b> {anomaly_results['num_anomalies']}<br/>
                    <b>Anomaly Percentage:</b> {anomaly_results['anomaly_percentage']:.2f}%<br/>
                    <b>Features Used:</b> {', '.join(anomaly_results['features_used'])}
                    """
                    elements.append(Paragraph(anomaly_text, self.styles['Normal']))
                    elements.append(Spacer(1, 20))
            
            # Coaching Insights
            coaching_insights = [v for k, v in analysis_results.items() if k.startswith('coaching_')]
            if coaching_insights:
                elements.append(Paragraph("Driver Coaching Insights", self.styles['SectionHeader']))
                elements.append(Spacer(1, 12))
                
                for coaching in coaching_insights:
                    if coaching.get('success'):
                        driver_header = f"<b>{coaching['driver_name']}</b> (Car #{coaching['driver_number']})"
                        elements.append(Paragraph(driver_header, self.styles['Normal']))
                        elements.append(Spacer(1, 6))
                        
                        for insight in coaching['insights']:
                            elements.append(Paragraph(f"• {insight}", self.styles['Insight']))
                        
                        elements.append(Spacer(1, 12))
            
            # Data Sample Table
            elements.append(PageBreak())
            elements.append(Paragraph("Data Sample (First 10 Rows)", self.styles['SectionHeader']))
            elements.append(Spacer(1, 12))
            
            # Select key columns for the table
            display_columns = []
            for col in ['POSITION', 'NUMBER', 'DRIVER', 'FL_TIME_SEC', 'FL_KPH', 'STATUS']:
                if col in data.columns:
                    display_columns.append(col)
            
            if display_columns:
                sample_data = data[display_columns].head(10)
                
                # Create table data
                table_data = [display_columns]  # Header row
                for idx, row in sample_data.iterrows():
                    table_data.append([str(row[col]) for col in display_columns])
                
                # Create table
                data_table = Table(table_data)
                data_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                elements.append(data_table)
            
            # Build PDF
            doc.build(elements)
            print(f"Successfully generated PDF report: {filepath}")
            return True
            
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            return False
