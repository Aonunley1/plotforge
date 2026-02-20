import pandas as pd
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QAction,
    QFileDialog,
    QMessageBox,
    QSplitter,
    QLabel,
)
from PyQt5.QtCore import Qt
import matplotlib.figure

from .config_panels.orchestrator import ConfigOrchestrator
from .config_panels.scatter_panel import ScatterConfigPanel
from .config_panels.line_panel import LineConfigPanel
from .config_panels.histogram_panel import HistogramConfigPanel
from .config_panels.bar_panel import BarPlotConfigPanel
from .config_panels.boxplot_panel import BoxPlotConfigPanel
from .plot_canvas import PlotCanvas
from .artifact_table import ArtifactTableView
from .controller import PlotController
from plotforge.config import BasePlotConfig, PlotResult


class MainWindow(QMainWindow):
    """
    Ref: SPEC-2A Section 1
    """

    # Constants for window resize calculations
    WINDOW_RESIZE_PADDING_WIDTH = 25
    WINDOW_RESIZE_PADDING_HEIGHT = 25

    def __init__(self):
        super().__init__()

        self.df: pd.DataFrame | None = None
        self.current_config: "BasePlotConfig | None" = None
        self.current_result: "PlotResult | None" = None

        # New State for Excel Reloading
        self.active_file_path: str | None = None

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
        load_action.triggered.connect(self.load_data_dialog)
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

        self.config_panel = ConfigOrchestrator()
        self.config_panel.register_panel("Scatter Plot", ScatterConfigPanel())
        self.config_panel.register_panel("Line Plot", LineConfigPanel())
        self.config_panel.register_panel("Histogram", HistogramConfigPanel())
        self.config_panel.register_panel("Bar Plot", BarPlotConfigPanel())
        self.config_panel.register_panel("Box Plot", BoxPlotConfigPanel())
        
        self.config_panel.update_signal.connect(self.handle_update_plot)
        self.config_panel.sheet_selected.connect(self.reload_excel_sheet)

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

    def load_data_dialog(self):
        """
        Opens file dialog and handles format selection logic.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Dataset",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)",
        )

        if not file_path:
            return

        try:
            self.active_file_path = file_path
            self.df = None
            sheet_names = []

            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path)
                # Clear sheet selector for CSVs
                if hasattr(self.config_panel, "update_sheet_selector"):
                    self.config_panel.update_sheet_selector([])
            else:
                # Excel Logic: Peek before load
                xls = pd.ExcelFile(file_path)
                sheet_names = xls.sheet_names

                # Push sheet names to ConfigPanel (Logic moved to Sidebar)
                if hasattr(self.config_panel, "update_sheet_selector"):
                    self.config_panel.update_sheet_selector(sheet_names)

                # Default to first sheet
                self.df = pd.read_excel(file_path, sheet_name=0)

            # Success Path
            if self.df is not None:
                self.status_label.setText(f"Loaded {len(self.df)} rows from {file_path}")
                columns = [str(c) for c in self.df.columns]
                self.config_panel.load_columns(columns)

        except Exception as e:
            QMessageBox.critical(self, "Error Loading Data", str(e))
            self.status_label.setText("Error loading data")
            self.active_file_path = None

    def reload_excel_sheet(self, sheet_name: str):
        """
        Slot called when the user changes the dropdown in ConfigPanel.
        """
        if not self.active_file_path:
            return

        try:
            self.setCursor(Qt.WaitCursor)
            self.status_label.setText(f"Switching to sheet: {sheet_name}...")

            self.df = pd.read_excel(self.active_file_path, sheet_name=sheet_name)

            columns = [str(c) for c in self.df.columns]
            self.config_panel.load_columns(columns)

            self.status_label.setText(f"Loaded sheet '{sheet_name}' ({len(self.df)} rows)")

            # Auto-trigger update? Optional.
            # self.handle_update_plot()

        except Exception as e:
            QMessageBox.critical(self, "Error Switching Sheet", str(e))
        finally:
            self.unsetCursor()

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

            # 2. Resize Window logic
            fig = self.current_result.figure
            wanted_width = fig.get_figwidth() * fig.get_dpi()
            wanted_height = fig.get_figheight() * fig.get_dpi()
            current_width = self.plot_canvas.width()
            current_height = self.plot_canvas.height()

            delta_w = max(0, int(wanted_width - current_width))
            delta_h = max(0, int(wanted_height - current_height))

            if delta_w > 0 or delta_h > 0:
                new_win_w = self.width() + delta_w + self.WINDOW_RESIZE_PADDING_WIDTH
                new_win_h = self.height() + delta_h + self.WINDOW_RESIZE_PADDING_HEIGHT
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
            QMessageBox.information(
                self, "No Artifacts", "No analysis data available to export."
            )
            return

        # Discover all exportable DataFrame artifacts dynamically.
        # This works for any current or future plot engine without modification.
        exportable: dict[str, pd.DataFrame] = {
            key: val
            for key, val in self.current_result.artifacts.items()
            if isinstance(val, pd.DataFrame) and not val.empty
        }

        if not exportable:
            QMessageBox.information(
                self, "No Data", "No tabular artifact data found in current plot."
            )
            return

        # If multiple artifact types exist, ask the user which one to export.
        if len(exportable) > 1:
            from PyQt5.QtWidgets import QInputDialog

            artifact_key, ok = QInputDialog.getItem(
                self,
                "Select Artifact",
                "Choose which artifact to export:",
                list(exportable.keys()),
                editable=False,
            )
            if not ok:
                return
        else:
            artifact_key = next(iter(exportable))

        df_to_save = exportable[artifact_key]
        default_filename = f"{artifact_key}.csv"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Artifacts", default_filename, "CSV Files (*.csv)"
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
            self,
            "Save Figure",
            "plot.png",
            "PNG Image (*.png);;PDF (*.pdf);;SVG (*.svg)",
        )

        if file_path:
            try:
                fig = self.current_result.figure
                dpi = self.current_config.save.dpi if self.current_config else 300

                # Save the figure exactly as rendered on screen.
                # constrained_layout has already computed the correct layout for
                # the screen dimensions — resizing the figure before save causes
                # the axes to degenerate (box plots collapse to a narrow strip).
                # bbox_inches='tight' trims any surrounding whitespace.
                fig.savefig(file_path, dpi=dpi, bbox_inches="tight")

                self.status_label.setText(f"Figure saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", str(e))


