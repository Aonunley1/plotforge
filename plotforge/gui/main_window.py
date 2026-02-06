import pandas as pd
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QAction, QFileDialog, QMessageBox, QSplitter, QLabel
)
from PyQt5.QtCore import Qt
import matplotlib.figure

from .config_panel import ConfigPanel
from .plot_canvas import PlotCanvas
from .artifact_table import ArtifactTableView
from .controller import PlotController
from plotforge.config import BasePlotConfig, PlotResult


class MainWindow(QMainWindow):
    """
    Ref: SPEC-2A Section 1
    """

    def __init__(self):
        super().__init__()

        self.df: pd.DataFrame | None = None
        self.current_config: 'BasePlotConfig' | None = None
        self.current_result: 'PlotResult' | None = None

        self.controller = PlotController()

        self.setWindowTitle("PlotForge - Config Driven Plotting")
        self.resize(1400, 900)

        self._create_menu_bar()
        self._create_layout()

        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)

    def _create_menu_bar(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")

        load_action = QAction("&Load Data...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_data)
        file_menu.addAction(load_action)

        export_action = QAction("&Export Artifacts...", self)
        export_action.triggered.connect(self.export_artifacts)
        file_menu.addAction(export_action)

        save_fig_action = QAction("&Save Figure...", self)
        save_fig_action.triggered.connect(self.save_figure)
        file_menu.addAction(save_fig_action)

    def _create_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)

        self.config_panel = ConfigPanel()
        self.config_panel.update_signal.connect(self.handle_update_plot)
        splitter.addWidget(self.config_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.plot_canvas = PlotCanvas()
        right_layout.addWidget(self.plot_canvas, stretch=4)

        self.artifact_table = ArtifactTableView()
        right_layout.addWidget(self.artifact_table, stretch=1)

        splitter.addWidget(right_panel)
        main_layout.addWidget(splitter)
        splitter.setSizes([450, 1000])

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Dataset", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )

        if not file_path: return

        try:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)

            self.status_label.setText(f"Loaded {len(self.df)} rows from {file_path}")

            columns = [str(c) for c in self.df.columns]
            self.config_panel.load_columns(columns)

        except Exception as e:
            QMessageBox.critical(self, "Error Loading Data", str(e))

    def handle_update_plot(self):
        if self.df is None:
            QMessageBox.warning(self, "No Data", "Please load a dataset first.")
            return

        try:
            self.status_label.setText("Rendering...")
            self.setCursor(Qt.WaitCursor)

            config = self.config_panel.build_config()
            self.current_config = config

            self.current_result = self.controller.execute(self.df, config)

            # 1. Update the Plot Canvas
            self.plot_canvas.set_figure(self.current_result.figure)

            # 2. Resize Window if necessary
            # We calculate the exact pixel size the figure wants to be
            fig = self.current_result.figure
            wanted_width = fig.get_figwidth() * fig.get_dpi()
            wanted_height = fig.get_figheight() * fig.get_dpi()

            # Get current size of the canvas widget
            current_width = self.plot_canvas.width()
            current_height = self.plot_canvas.height()

            # Calculate how much we need to grow
            # (We only grow, we don't shrink, to avoid jarring jumps)
            delta_w = max(0, int(wanted_width - current_width))
            delta_h = max(0, int(wanted_height - current_height))

            # If the plot is bigger than the available space, expand the MainWindow
            if delta_w > 0 or delta_h > 0:
                # Add a small buffer for borders (e.g., 25px)
                new_win_w = self.width() + delta_w + 25
                new_win_h = self.height() + delta_h + 25
                self.resize(new_win_w, new_win_h)

            # 3. Update Artifacts
            self.artifact_table.set_artifacts(self.current_result.artifacts)

            if self.current_result.warnings:
                warning_msg = "\n".join(self.current_result.warnings)
                QMessageBox.warning(self, "Plot Warnings", warning_msg)

            self.status_label.setText("Render Complete")

        except Exception as e:
            QMessageBox.critical(self, "Plotting Error", str(e))
            self.status_label.setText("Error during render")
        finally:
            self.unsetCursor()

    def export_artifacts(self):
        if not self.current_result or not self.current_result.artifacts:
            QMessageBox.information(self, "No Artifacts", "No analysis data available to export.")
            return

        df_to_save = self.current_result.artifacts.get("trendlines")

        if df_to_save is None:
            QMessageBox.information(self, "No Data", "No trendline data found in current plot.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Artifacts", "trendlines.csv", "CSV Files (*.csv)"
        )

        if file_path:
            try:
                df_to_save.to_csv(file_path, index=False)
                self.status_label.setText(f"Artifacts exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def save_figure(self):
        if not self.current_result or not self.current_result.figure:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Figure", "plot.png", "PNG Image (*.png);;PDF (*.pdf);;SVG (*.svg)"
        )

        if file_path:
            try:
                self.current_result.figure.savefig(file_path, dpi=300)
                self.status_label.setText(f"Figure saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", str(e))