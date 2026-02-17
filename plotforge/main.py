import sys
import matplotlib

# Force Matplotlib to use the Qt5 backend before importing pyplot
matplotlib.use("Qt5Agg")

from PyQt5.QtWidgets import QApplication
from plotforge.gui.main_window import MainWindow
from plotforge.gui.styles import MAIN_STYLESHEET

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(MAIN_STYLESHEET)

    # Initialize and show the main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())