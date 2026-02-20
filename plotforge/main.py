import sys
import warnings
import matplotlib

# Force Matplotlib to use the Qt5 backend before importing pyplot.
matplotlib.use("Qt5Agg")

# Suppress known font-related warnings from matplotlib/seaborn that can
# appear as console noise (or, on some Windows setups, as dialog boxes)
# during the first run when the font cache is being built.
warnings.filterwarnings("ignore", message=".*Glyph.*missing from font.*")
warnings.filterwarnings("ignore", message=".*findfont.*")
warnings.filterwarnings("ignore", message=".*Font family.*not found.*")

from PyQt5.QtWidgets import QApplication
from plotforge.gui.main_window import MainWindow
from plotforge.gui.styles import MAIN_STYLESHEET

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(MAIN_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())