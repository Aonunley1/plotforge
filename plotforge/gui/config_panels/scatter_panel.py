from typing import Optional, List
from PyQt5.QtWidgets import (
    QFormLayout,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QLabel,
    QHBoxLayout,
)

from plotforge.config import (
    ScatterPlotConfig,
    TrendlineConfig,
    KDEConfig,
    CIConfig,
    StatisticalOverlayConfig,
    DEFAULT_PALETTE,
    DEFAULT_MARKERS,
)
from plotforge.gui.config_panels.base_panel import BaseConfigPanel, CollapsibleBox


class ScatterConfigPanel(BaseConfigPanel):
    """
    Configuration panel for Scatter Plots.
    Inherits shared UI from BaseConfigPanel and adds scatter-specific options and overlays.
    """
    def __init__(self, parent: Optional[BaseConfigPanel] = None):
        super().__init__(parent)
        self._add_scatter_specific_ui()

    def _add_scatter_specific_ui(self):
        # 1. Scatter Options
        scatter_group = CollapsibleBox("Scatter Options", expanded=True)
        scatter_layout = QFormLayout()

        self.spin_size = QDoubleSpinBox()
        self.spin_size.setValue(100.0)
        self.spin_size.setRange(1.0, 500.0)

        self.spin_alpha = QDoubleSpinBox()
        self.spin_alpha.setValue(0.8)
        self.spin_alpha.setRange(0.0, 1.0)
        self.spin_alpha.setSingleStep(0.1)

        self.spin_linewidth = QDoubleSpinBox()
        self.spin_linewidth.setValue(1.0)
        self.spin_linewidth.setRange(0.0, 10.0)

        self.combo_edgecolor = QComboBox()
        self.combo_edgecolor.addItems(["black", "white", "none", "gray", "red", "blue"])

        self.combo_palette = self._build_palette_combo(
            default_label="Custom (Blue/Red/Green/Orange)", default_data="custom"
        )

        self.combo_markers = QComboBox()
        self.combo_markers.addItem("Custom (o, X, ^, s)", "custom")
        self.combo_markers.addItem("Auto (Seaborn Default)", "auto")

        scatter_layout.addRow("Marker Size:", self.spin_size)
        scatter_layout.addRow("Opacity:", self.spin_alpha)
        scatter_layout.addRow("Edge Width:", self.spin_linewidth)
        scatter_layout.addRow("Edge Color:", self.combo_edgecolor)
        scatter_layout.addRow("Palette:", self.combo_palette)
        scatter_layout.addRow("Markers:", self.combo_markers)
        scatter_group.setLayout(scatter_layout)

        # 2. Statistical Overlays (Scatter Specific)
        stats_group = CollapsibleBox("Statistical Overlays", expanded=False)
        stats_layout = QFormLayout()

        # Trendline
        self.check_trendline = QCheckBox("Enable Trendline")
        self.check_trendline.toggled.connect(self._toggle_trendline_options)

        self.spin_order = QDoubleSpinBox() # Changed to double to allow more flexibility if needed, but logic uses int
        self.spin_order.setDecimals(0)
        self.spin_order.setValue(1)
        self.spin_order.setEnabled(False)

        self.spin_trend_alpha = QDoubleSpinBox()
        self.spin_trend_alpha.setValue(1.0)
        self.spin_trend_alpha.setRange(0.0, 1.0)
        self.spin_trend_alpha.setEnabled(False)

        self.check_limit_range = QCheckBox("Limit Fit Range")
        self.check_limit_range.setEnabled(False)
        self.check_limit_range.toggled.connect(self._toggle_range_options)

        range_layout = QHBoxLayout()
        self.spin_fit_min = QDoubleSpinBox()
        self.spin_fit_max = QDoubleSpinBox()
        self.spin_fit_min.setRange(-1e6, 1e6)
        self.spin_fit_max.setRange(-1e6, 1e6)
        self.spin_fit_max.setValue(100.0)
        self.spin_fit_min.setEnabled(False)
        self.spin_fit_max.setEnabled(False)
        range_layout.addWidget(QLabel("Min:"))
        range_layout.addWidget(self.spin_fit_min)
        range_layout.addWidget(QLabel("Max:"))
        range_layout.addWidget(self.spin_fit_max)

        # Confidence Interval
        ci_layout = QHBoxLayout()
        self.check_ci = QCheckBox("Show CI")
        self.check_ci.setEnabled(False)
        self.check_ci.toggled.connect(self._toggle_ci_options)
        self.spin_ci_level = QDoubleSpinBox()
        self.spin_ci_level.setRange(0.50, 0.99)
        self.spin_ci_level.setValue(0.95)
        self.spin_ci_level.setEnabled(False)
        ci_layout.addWidget(self.check_ci)
        ci_layout.addWidget(QLabel("Lvl:"))
        ci_layout.addWidget(self.spin_ci_level)

        # KDE
        self.check_kde = QCheckBox("Enable KDE")
        self.check_kde.toggled.connect(self._toggle_kde_options)
        self.combo_kde_cmap = QComboBox()
        self.combo_kde_cmap.addItems(["mako", "rocket", "flare", "magma", "viridis"])
        self.combo_kde_cmap.setEnabled(False)

        stats_layout.addRow(self.check_trendline)
        stats_layout.addRow("Order:", self.spin_order)
        stats_layout.addRow("Alpha:", self.spin_trend_alpha)
        stats_layout.addRow(self.check_limit_range)
        stats_layout.addRow(range_layout)
        stats_layout.addRow(ci_layout)
        stats_layout.addRow(self.check_kde)
        stats_layout.addRow("KDE Cmap:", self.combo_kde_cmap)
        stats_group.setLayout(stats_layout)

        # Add to the reserved placeholder in BaseConfigPanel
        self.plot_options_container.addWidget(scatter_group)
        self.plot_options_container.addWidget(stats_group)

    def _toggle_trendline_options(self, checked):
        self.spin_order.setEnabled(checked)
        self.spin_trend_alpha.setEnabled(checked)
        self.check_limit_range.setEnabled(checked)
        self.check_ci.setEnabled(checked)
        if not checked:
            self._toggle_range_options(False)
            self._toggle_ci_options(False)

    def _toggle_range_options(self, checked):
        self.spin_fit_min.setEnabled(checked)
        self.spin_fit_max.setEnabled(checked)

    def _toggle_ci_options(self, checked):
        self.spin_ci_level.setEnabled(checked)

    def _toggle_kde_options(self, checked):
        self.combo_kde_cmap.setEnabled(checked)

    def build_config(self) -> ScatterPlotConfig:
        base_data = self.build_base_config_data()
        
        # Trendline
        fit_range = None
        if self.check_limit_range.isChecked():
            fit_range = (self.spin_fit_min.value(), self.spin_fit_max.value())
            
        trendline = TrendlineConfig(
            enabled=self.check_trendline.isChecked(),
            order=int(self.spin_order.value()),
            alpha=self.spin_trend_alpha.value(),
            fit_range=fit_range,
        )

        ci = CIConfig(enabled=self.check_ci.isChecked(), level=self.spin_ci_level.value())
        kde = KDEConfig(enabled=self.check_kde.isChecked(), cmap=self.combo_kde_cmap.currentText())

        palette_val = self.combo_palette.currentData()
        final_palette = DEFAULT_PALETTE if palette_val == "custom" else self.combo_palette.currentText()
        
        marker_val = self.combo_markers.currentData()
        final_markers = DEFAULT_MARKERS if marker_val == "custom" else True

        return ScatterPlotConfig(
            **base_data,
            marker_size=self.spin_size.value(),
            alpha=self.spin_alpha.value(),
            linewidth=self.spin_linewidth.value(),
            edgecolor=self.combo_edgecolor.currentText(),
            palette=final_palette,
            markers=final_markers,
            overlays=StatisticalOverlayConfig(trendline=trendline, kde=kde, ci=ci),
        )
