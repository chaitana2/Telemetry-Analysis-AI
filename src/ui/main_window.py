from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt
import sys
import os

# Add src to path to import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.core.data_loader import DataLoader

class MainWindow(QMainWindow):
    """
    The main application window for the Telemetry Analysis Tool.

    Inherits from PyQt6.QtWidgets.QMainWindow.
    """
    def __init__(self):
        """Initialize the main window, set title, size, and load UI."""
        super().__init__()
        self.setWindowTitle("Telemetry Analysis Tool")
        self.resize(1200, 800)

        self.data_loader = DataLoader()
        self.data = None

        self.init_ui()

    def init_ui(self):
        """Sets up the user interface components (layout, buttons, tabs)."""
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Top Bar (Import Button)
        top_bar = QHBoxLayout()
        self.import_btn = QPushButton("Import CSV")
        self.import_btn.clicked.connect(self.import_csv)
        top_bar.addWidget(self.import_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Data View
        self.data_tab = QWidget()
        self.data_tab_layout = QVBoxLayout(self.data_tab)
        self.data_table = QTableWidget()
        self.data_tab_layout.addWidget(self.data_table)
        self.tabs.addTab(self.data_tab, "Data View")

        # Tab 2: Dashboard (Placeholder)
        self.dashboard_tab = QWidget()
        self.dashboard_layout = QVBoxLayout(self.dashboard_tab)
        self.dashboard_label = QLabel("Dashboard - Visualizations will appear here")
        self.dashboard_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dashboard_layout.addWidget(self.dashboard_label)
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

    def import_csv(self):
        """
        Opens a file dialog to select a CSV file and loads it.
        
        Displays a success or error message based on the loading result.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            if self.data_loader.load_csv(file_path):
                self.data = self.data_loader.preprocess()
                self.populate_table()
                QMessageBox.information(self, "Success", "Data loaded successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to load CSV.")

    def populate_table(self):
        """
        Populates the data table with the loaded dataframe content.
        """
        if self.data is None:
            return

        df = self.data
        self.data_table.setRowCount(df.shape[0])
        self.data_table.setColumnCount(df.shape[1])
        self.data_table.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.data_table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

