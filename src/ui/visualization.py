"""
Visualization module for telemetry data charts.

This module provides PyQt6-compatible matplotlib charts for displaying
telemetry data including lap times, gaps, speeds, and positions.
"""

import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QScrollArea, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns


class BaseChart(QWidget):
    """
    Base class for all chart widgets.
    
    Provides common functionality for matplotlib integration with PyQt6.
    """
    
    def __init__(self, parent=None):
        """Initialize the base chart widget."""
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Apply seaborn style
        sns.set_style("darkgrid")
        
    def clear(self):
        """Clear the chart."""
        self.ax.clear()
        self.canvas.draw()


class LapTimeChart(BaseChart):
    """
    Line chart showing lap time progression for drivers.
    
    Displays lap times over the course of a race session with
    different colors for each driver.
    """
    
    def __init__(self, parent=None):
        """Initialize the lap time chart."""
        super().__init__(parent)
        self.anomaly_indices = []
        
    def plot(self, df: pd.DataFrame, anomaly_indices=None):
        """
        Plot lap time progression.
        
        Args:
            df (pd.DataFrame): Telemetry dataframe with FL_TIME_SEC column.
            anomaly_indices (list, optional): Indices of anomalous data points.
        """
        self.ax.clear()
        
        if df is None or df.empty:
            self.ax.text(0.5, 0.5, 'No data available', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        # Check if we have the required columns
        if 'FL_TIME_SEC' not in df.columns:
            self.ax.text(0.5, 0.5, 'FL_TIME_SEC column not found', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        # Group by driver and plot
        if 'DRIVER' in df.columns and 'NUMBER' in df.columns:
            for driver_num in df['NUMBER'].unique():
                driver_data = df[df['NUMBER'] == driver_num].copy()
                driver_data = driver_data.sort_index()
                
                # Get driver name
                driver_name = driver_data['DRIVER'].iloc[0] if not driver_data.empty else f"Car #{driver_num}"
                
                # Plot lap times
                valid_data = driver_data[driver_data['FL_TIME_SEC'].notna()]
                if not valid_data.empty:
                    self.ax.plot(valid_data.index, valid_data['FL_TIME_SEC'], 
                               marker='o', label=driver_name, linewidth=2, markersize=6)
        else:
            # Simple plot if driver info not available
            valid_data = df[df['FL_TIME_SEC'].notna()]
            if not valid_data.empty:
                self.ax.plot(valid_data.index, valid_data['FL_TIME_SEC'], 
                           marker='o', linewidth=2, markersize=6)
        
        # Highlight anomalies
        if anomaly_indices:
            self.anomaly_indices = anomaly_indices
            for idx in anomaly_indices:
                if idx < len(df) and pd.notna(df.iloc[idx]['FL_TIME_SEC']):
                    self.ax.plot(idx, df.iloc[idx]['FL_TIME_SEC'], 
                               'ro', markersize=12, markerfacecolor='none', 
                               markeredgewidth=2, label='Anomaly' if idx == anomaly_indices[0] else '')
        
        self.ax.set_xlabel('Data Point Index', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Lap Time (seconds)', fontsize=12, fontweight='bold')
        self.ax.set_title('Lap Time Progression', fontsize=14, fontweight='bold')
        self.ax.legend(loc='best')
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()


class GapAnalysisChart(BaseChart):
    """
    Multi-line chart showing gaps to leader over time.
    
    Visualizes how the gap between drivers and the leader evolves.
    """
    
    def __init__(self, parent=None):
        """Initialize the gap analysis chart."""
        super().__init__(parent)
        
    def plot(self, df: pd.DataFrame):
        """
        Plot gap analysis.
        
        Args:
            df (pd.DataFrame): Telemetry dataframe with GAP_FIRST_SEC column.
        """
        self.ax.clear()
        
        if df is None or df.empty:
            self.ax.text(0.5, 0.5, 'No data available', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        if 'GAP_FIRST_SEC' not in df.columns:
            self.ax.text(0.5, 0.5, 'GAP_FIRST_SEC column not found', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        # Plot gaps by driver
        if 'DRIVER' in df.columns and 'NUMBER' in df.columns:
            for driver_num in df['NUMBER'].unique():
                driver_data = df[df['NUMBER'] == driver_num].copy()
                driver_data = driver_data.sort_index()
                
                driver_name = driver_data['DRIVER'].iloc[0] if not driver_data.empty else f"Car #{driver_num}"
                
                valid_data = driver_data[driver_data['GAP_FIRST_SEC'].notna()]
                if not valid_data.empty:
                    self.ax.plot(valid_data.index, valid_data['GAP_FIRST_SEC'], 
                               marker='o', label=driver_name, linewidth=2, markersize=6)
        else:
            valid_data = df[df['GAP_FIRST_SEC'].notna()]
            if not valid_data.empty:
                self.ax.plot(valid_data.index, valid_data['GAP_FIRST_SEC'], 
                           marker='o', linewidth=2, markersize=6)
        
        self.ax.set_xlabel('Data Point Index', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Gap to Leader (seconds)', fontsize=12, fontweight='bold')
        self.ax.set_title('Gap Analysis', fontsize=14, fontweight='bold')
        self.ax.legend(loc='best')
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()


class SpeedDistributionChart(BaseChart):
    """
    Histogram showing distribution of fastest lap speeds.
    
    Displays the frequency distribution of top speeds achieved.
    """
    
    def __init__(self, parent=None):
        """Initialize the speed distribution chart."""
        super().__init__(parent)
        
    def plot(self, df: pd.DataFrame):
        """
        Plot speed distribution histogram.
        
        Args:
            df (pd.DataFrame): Telemetry dataframe with FL_KPH column.
        """
        self.ax.clear()
        
        if df is None or df.empty:
            self.ax.text(0.5, 0.5, 'No data available', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        if 'FL_KPH' not in df.columns:
            self.ax.text(0.5, 0.5, 'FL_KPH column not found', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        speeds = df['FL_KPH'].dropna()
        
        if speeds.empty:
            self.ax.text(0.5, 0.5, 'No speed data available', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        # Create histogram
        self.ax.hist(speeds, bins=15, color='skyblue', edgecolor='black', alpha=0.7)
        
        # Add mean line
        mean_speed = speeds.mean()
        self.ax.axvline(mean_speed, color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {mean_speed:.1f} km/h')
        
        self.ax.set_xlabel('Speed (km/h)', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        self.ax.set_title('Speed Distribution', fontsize=14, fontweight='bold')
        self.ax.legend(loc='best')
        self.ax.grid(True, alpha=0.3, axis='y')
        self.figure.tight_layout()
        self.canvas.draw()


class PositionChart(BaseChart):
    """
    Line chart showing position changes over time.
    
    Visualizes how driver positions change throughout the session.
    """
    
    def __init__(self, parent=None):
        """Initialize the position chart."""
        super().__init__(parent)
        
    def plot(self, df: pd.DataFrame):
        """
        Plot position changes.
        
        Args:
            df (pd.DataFrame): Telemetry dataframe with POSITION column.
        """
        self.ax.clear()
        
        if df is None or df.empty:
            self.ax.text(0.5, 0.5, 'No data available', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        if 'POSITION' not in df.columns:
            self.ax.text(0.5, 0.5, 'POSITION column not found', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        # Plot position by driver
        if 'DRIVER' in df.columns and 'NUMBER' in df.columns:
            for driver_num in df['NUMBER'].unique():
                driver_data = df[df['NUMBER'] == driver_num].copy()
                driver_data = driver_data.sort_index()
                
                driver_name = driver_data['DRIVER'].iloc[0] if not driver_data.empty else f"Car #{driver_num}"
                
                valid_data = driver_data[driver_data['POSITION'].notna()]
                if not valid_data.empty:
                    self.ax.plot(valid_data.index, valid_data['POSITION'], 
                               marker='o', label=driver_name, linewidth=2, markersize=6)
        else:
            valid_data = df[df['POSITION'].notna()]
            if not valid_data.empty:
                self.ax.plot(valid_data.index, valid_data['POSITION'], 
                           marker='o', linewidth=2, markersize=6)
        
        self.ax.set_xlabel('Data Point Index', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Position', fontsize=12, fontweight='bold')
        self.ax.set_title('Position Changes', fontsize=14, fontweight='bold')
        self.ax.invert_yaxis()  # Position 1 at top
        self.ax.legend(loc='best')
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()


class DynamicChart(BaseChart):
    """
    Generic chart for plotting any two parameters.
    """
    
    def __init__(self, parent=None):
        """Initialize the dynamic chart."""
        super().__init__(parent)
        
    def plot(self, df: pd.DataFrame, x_col: str, y_col: str, chart_type: str = 'line'):
        """
        Plot data based on selected columns.
        
        Args:
            df (pd.DataFrame): Dataframe.
            x_col (str): Column for X axis.
            y_col (str): Column for Y axis.
            chart_type (str): 'line', 'scatter', or 'bar'.
        """
        self.ax.clear()
        
        if df is None or df.empty:
            self.ax.text(0.5, 0.5, 'No data available', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
            
        if x_col not in df.columns or y_col not in df.columns:
            self.ax.text(0.5, 0.5, f'Columns not found: {x_col}, {y_col}', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
            
        # Plot by driver if available
        if 'DRIVER' in df.columns and 'NUMBER' in df.columns:
            for driver_num in df['NUMBER'].unique():
                driver_data = df[df['NUMBER'] == driver_num].copy()
                
                # Sort by X if it's time-based or sequential
                if pd.api.types.is_numeric_dtype(driver_data[x_col]):
                    driver_data = driver_data.sort_values(x_col)
                
                driver_name = driver_data['DRIVER'].iloc[0] if not driver_data.empty else f"Car #{driver_num}"
                
                valid_data = driver_data.dropna(subset=[x_col, y_col])
                
                if not valid_data.empty:
                    if chart_type == 'line':
                        self.ax.plot(valid_data[x_col], valid_data[y_col], 
                                   marker='o', label=driver_name, linewidth=2, markersize=4)
                    elif chart_type == 'scatter':
                        self.ax.scatter(valid_data[x_col], valid_data[y_col], 
                                      label=driver_name, alpha=0.7)
                    elif chart_type == 'bar':
                        self.ax.bar(valid_data[x_col], valid_data[y_col], 
                                  label=driver_name, alpha=0.7)
        else:
            valid_data = df.dropna(subset=[x_col, y_col])
            if not valid_data.empty:
                if chart_type == 'line':
                    self.ax.plot(valid_data[x_col], valid_data[y_col], marker='o')
                elif chart_type == 'scatter':
                    self.ax.scatter(valid_data[x_col], valid_data[y_col])
                elif chart_type == 'bar':
                    self.ax.bar(valid_data[x_col], valid_data[y_col])
        
        self.ax.set_xlabel(x_col, fontsize=12, fontweight='bold')
        self.ax.set_ylabel(y_col, fontsize=12, fontweight='bold')
        self.ax.set_title(f'{y_col} vs {x_col}', fontsize=14, fontweight='bold')
        
        if chart_type != 'bar':
            self.ax.grid(True, alpha=0.3)
            
        if 'DRIVER' in df.columns:
            self.ax.legend(loc='best')
            
        self.figure.tight_layout()
        self.canvas.draw()


class SmartDashboard(QWidget):
    """
    AI-driven dashboard that automatically generates relevant charts
    based on the available data columns.
    """
    
    def __init__(self, parent=None):
        """Initialize the smart dashboard."""
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QGridLayout(self.content_widget)
        self.scroll.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll)
        
        self.charts = []
        
    def generate_dashboard(self, df: pd.DataFrame):
        """
        Analyze data and generate the most relevant charts automatically.
        
        Args:
            df (pd.DataFrame): The telemetry data.
        """
        # Clear existing charts
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().setParent(None)
        self.charts = []
        
        if df is None or df.empty:
            return

        columns = [c.upper() for c in df.columns]
        col_map = {c.upper(): c for c in df.columns}
        
        # 1. Identify Key Columns using heuristics
        time_col = next((c for c in columns if 'TIME' in c or 'SESSION' in c), None)
        lap_col = next((c for c in columns if 'LAP' in c and 'TIME' not in c), None)
        speed_col = next((c for c in columns if 'SPEED' in c or 'KPH' in c or 'MPH' in c), None)
        pos_col = next((c for c in columns if 'POS' in c), None)
        throttle_col = next((c for c in columns if 'THROT' in c or 'PEDAL' in c), None)
        brake_col = next((c for c in columns if 'BRAKE' in c), None)
        rpm_col = next((c for c in columns if 'RPM' in c or 'ENGINE' in c), None)
        gear_col = next((c for c in columns if 'GEAR' in c), None)
        
        charts_to_create = []
        
        # 2. AI Decision Logic: Determine best visualizations
        
        # A. Speed Trace (Speed vs Time/Distance)
        if speed_col and time_col:
            charts_to_create.append({
                'title': 'Speed Trace',
                'x': col_map[time_col],
                'y': col_map[speed_col],
                'type': 'line'
            })
            
        # B. Lap Time Progression (Lap Time vs Lap Number)
        # Assuming we have a lap time column (often same as time_col if it's 'LAP_TIME')
        lap_time_col = next((c for c in columns if 'LAP' in c and 'TIME' in c), None)
        if lap_time_col and lap_col:
            charts_to_create.append({
                'title': 'Lap Time Progression',
                'x': col_map[lap_col],
                'y': col_map[lap_time_col],
                'type': 'line'
            })
        elif lap_time_col:
             # If no explicit lap number, use index
             charts_to_create.append({
                'title': 'Lap Time Distribution',
                'x': col_map[lap_time_col], # Histogram logic handled by chart type or pre-processing
                'y': col_map[lap_time_col],
                'type': 'bar' # Placeholder for distribution
            })

        # C. Driver Position Changes
        if pos_col and (lap_col or time_col):
            charts_to_create.append({
                'title': 'Position History',
                'x': col_map[lap_col] if lap_col else col_map[time_col],
                'y': col_map[pos_col],
                'type': 'line'
            })
            
        # D. Telemetry Overview (Throttle/Brake vs Time)
        if throttle_col and time_col:
             charts_to_create.append({
                'title': 'Throttle Application',
                'x': col_map[time_col],
                'y': col_map[throttle_col],
                'type': 'line'
            })
            
        if brake_col and time_col:
             charts_to_create.append({
                'title': 'Braking Profile',
                'x': col_map[time_col],
                'y': col_map[brake_col],
                'type': 'line'
            })

        # E. Engine Performance (RPM vs Speed)
        if rpm_col and speed_col:
            charts_to_create.append({
                'title': 'Gearing Analysis (RPM vs Speed)',
                'x': col_map[speed_col],
                'y': col_map[rpm_col],
                'type': 'scatter'
            })

        # 3. Generate Layout
        row = 0
        col = 0
        max_cols = 2
        
        for chart_info in charts_to_create:
            chart_widget = DynamicChart()
            chart_widget.plot(df, chart_info['x'], chart_info['y'], chart_info['type'])
            chart_widget.ax.set_title(chart_info['title'], fontsize=12, fontweight='bold')
            chart_widget.canvas.draw()
            
            self.content_layout.addWidget(chart_widget, row, col)
            self.charts.append(chart_widget)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # If no specific charts matched, just plot first 2 numeric columns
        if not charts_to_create:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                chart_widget = DynamicChart()
                chart_widget.plot(df, numeric_cols[0], numeric_cols[1], 'scatter')
                self.content_layout.addWidget(chart_widget, 0, 0)
