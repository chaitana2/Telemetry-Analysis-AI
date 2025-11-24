import sys
import os
from PyQt6.QtWidgets import QApplication

# Add src to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Apply a dark theme style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
