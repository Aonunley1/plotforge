from typing import Optional
from PyQt5.QtWidgets import (
    QFormLayout,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QSpinBox,
    QHBoxLayout,
)

from plotforge.config import HistogramConfig, StatisticalOverlayConfig, DEFAULT_PALETTE
from plotforge.gui.config_panels.base_panel import BaseConfigPanel, CollapsibleBox


class HistogramConfigPanel(BaseConfigPanel):
    """
    Configuration panel for Histogram Plots.
    Inherits shared UI from BaseConfigPanel but hides irrelevant fields (Y-Axis, Style-By).
    """
    def __init__(self, parent: Optional[BaseConfigPanel] = None):
        super().__init__(parent)
        self._add_histogram_specific_ui()
        self._hide_irrelevant_base_fields()

    def _hide_irrelevant_base_fields(self):
        """Hides Y-Axis and Style-By selectors as they aren't used for standard histograms."""
        layout = self.data_group.layout()
        if isinstance(layout, QFormLayout):
            # Iterate to find rows with specific widgets
            for i in range(layout.rowCount()):
                item = layout.itemAt(i, QFormLayout.FieldRole)
                if not item:
                    continue
                widget = item.widget()
                if widget == self.combo_y or widget == self.combo_style:
                    layout.setRowVisible(i, False)

    def _add_histogram_specific_ui(self):
        # Histogram Options
        hist_group = CollapsibleBox("Histogram Options", expanded=True)
        hist_layout = QFormLayout()

        # Bins
        self.check_auto_bins = QCheckBox("Auto Bins")
        self.check_auto_bins.setChecked(True)
        self.spin_bins = QSpinBox()
        self.spin_bins.setRange(1, 1000)
        self.spin_bins.setValue(30)
        self.spin_bins.setEnabled(False)
        self.check_auto_bins.toggled.connect(lambda checked: self.spin_bins.setEnabled(not checked))
        
        bins_layout = QHBoxLayout()
        bins_layout.addWidget(self.check_auto_bins)
        bins_layout.addWidget(self.spin_bins)

        # Stat
        self.combo_stat = QComboBox()
        self.combo_stat.addItems(["count", "frequency", "probability", "percent", "density"])
        
        # Element
        self.combo_element = QComboBox()
        self.combo_element.addItems(["bars", "step", "poly"])
        
        # Flags
        self.check_kde = QCheckBox("Show KDE")
        self.check_cumulative = QCheckBox("Cumulative")
        self.check_fill = QCheckBox("Fill Bars")
        self.check_fill.setChecked(True)
        self.check_log = QCheckBox("Log Scale")
        
        # Styling
        self.spin_alpha = QDoubleSpinBox()
        self.spin_alpha.setRange(0.0, 1.0)
        self.spin_alpha.setSingleStep(0.1)
        self.spin_alpha.setValue(0.5)
        
        self.spin_linewidth = QDoubleSpinBox()
        self.spin_linewidth.setRange(0.0, 10.0)
        self.spin_linewidth.setValue(0.0)
        
        self.combo_palette = QComboBox()
        self.combo_palette.addItem("Default", "default")
        self.combo_palette.addItems(["deep", "muted", "bright", "pastel", "dark", "colorblind"])

        hist_layout.addRow("Bins:", bins_layout)
        hist_layout.addRow("Statistic:", self.combo_stat)
        hist_layout.addRow("Visual Style:", self.combo_element)
        hist_layout.addRow(self.check_kde)
        hist_layout.addRow(self.check_cumulative)
        hist_layout.addRow(self.check_fill)
        hist_layout.addRow(self.check_log)
        hist_layout.addRow("Opacity:", self.spin_alpha)
        hist_layout.addRow("Edge Width:", self.spin_linewidth)
        hist_layout.addRow("Palette:", self.combo_palette)
        
        hist_group.setLayout(hist_layout)
        self.plot_options_container.addWidget(hist_group)

    def build_config(self) -> HistogramConfig:
        base_data = self.build_base_config_data()
        
        # Remove fields not present in HistogramConfig
        if "y" in base_data: del base_data["y"]
        if "style_by" in base_data: del base_data["style_by"]
        
        bins_val = "auto"
        if not self.check_auto_bins.isChecked():
            bins_val = self.spin_bins.value()
            
        palette_val = self.combo_palette.currentData()
        final_palette = DEFAULT_PALETTE if palette_val == "default" else self.combo_palette.currentText()

        return HistogramConfig(
            **base_data,
            bins=bins_val,
            stat=self.combo_stat.currentText(),
            kde=self.check_kde.isChecked(),
            cumulative=self.check_cumulative.isChecked(),
            element=self.combo_element.currentText(),
            fill=self.check_fill.isChecked(),
            log_scale=self.check_log.isChecked(),
            alpha=self.spin_alpha.value(),
            linewidth=self.spin_linewidth.value(),
            palette=final_palette,
            overlays=StatisticalOverlayConfig() # Empty overlays for now
        )
