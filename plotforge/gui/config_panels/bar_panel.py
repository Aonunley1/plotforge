from typing import Optional
from PyQt5.QtWidgets import (
    QFormLayout,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QLabel,
    QHBoxLayout,
)

from plotforge.config import BarPlotConfig, StatisticalOverlayConfig, DEFAULT_PALETTE
from plotforge.gui.config_panels.base_panel import BaseConfigPanel, CollapsibleBox


class BarPlotConfigPanel(BaseConfigPanel):
    """
    Configuration panel for Bar Plots.
    Inherits shared UI from BaseConfigPanel.
    """
    def __init__(self, parent: Optional[BaseConfigPanel] = None):
        super().__init__(parent)
        self._add_bar_specific_ui()

    def _add_bar_specific_ui(self):
        # Bar Options
        bar_group = CollapsibleBox("Bar Options", expanded=True)
        bar_layout = QFormLayout()

        # Orientation
        self.combo_orient = QComboBox()
        self.combo_orient.addItem("Vertical (x=Cat, y=Val)", "v")
        self.combo_orient.addItem("Horizontal (y=Cat, x=Val)", "h")
        
        # Aggregation
        self.combo_estimator = QComboBox()
        self.combo_estimator.addItems(["mean", "median", "sum", "min", "max", "count"])
        
        # Error Bars
        self.combo_errorbar = QComboBox()
        self.combo_errorbar.addItem("Confidence Interval (95%)", "ci")
        self.combo_errorbar.addItem("Standard Deviation", "sd")
        self.combo_errorbar.addItem("Standard Error", "se")
        self.combo_errorbar.addItem("Percentile Interval", "pi")
        self.combo_errorbar.addItem("None", "none")
        
        self.spin_capsize = QDoubleSpinBox()
        self.spin_capsize.setRange(0.0, 1.0)
        self.spin_capsize.setSingleStep(0.05)
        self.spin_capsize.setValue(0.1)
        
        # Visuals
        self.spin_width = QDoubleSpinBox()
        self.spin_width.setRange(0.1, 1.0)
        self.spin_width.setValue(0.8)
        self.spin_width.setSingleStep(0.1)
        
        self.spin_alpha = QDoubleSpinBox()
        self.spin_alpha.setRange(0.0, 1.0)
        self.spin_alpha.setSingleStep(0.1)
        self.spin_alpha.setValue(0.8)
        
        self.spin_linewidth = QDoubleSpinBox()
        self.spin_linewidth.setRange(0.0, 5.0)
        self.spin_linewidth.setValue(0.0)
        
        self.combo_edgecolor = QComboBox()
        self.combo_edgecolor.addItems(["none", "black", "white", "gray"])
        
        self.combo_palette = QComboBox()
        self.combo_palette.addItem("Default", "default")
        self.combo_palette.addItems(["deep", "muted", "bright", "pastel", "dark", "colorblind"])

        bar_layout.addRow("Orientation:", self.combo_orient)
        bar_layout.addRow("Estimator:", self.combo_estimator)
        bar_layout.addRow("Error Bar:", self.combo_errorbar)
        bar_layout.addRow("Capsize:", self.spin_capsize)
        bar_layout.addRow("Bar Width:", self.spin_width)
        bar_layout.addRow("Opacity:", self.spin_alpha)
        bar_layout.addRow("Edge Width:", self.spin_linewidth)
        bar_layout.addRow("Edge Color:", self.combo_edgecolor)
        bar_layout.addRow("Palette:", self.combo_palette)
        
        bar_group.setLayout(bar_layout)
        self.plot_options_container.addWidget(bar_group)

    def build_config(self) -> BarPlotConfig:
        base_data = self.build_base_config_data()
        
        palette_val = self.combo_palette.currentData()
        final_palette = DEFAULT_PALETTE if palette_val == "default" else self.combo_palette.currentText()
        
        errorbar_val = self.combo_errorbar.currentData()
        
        # Fix: If user selects None in errorbar, pass None directly? 
        # Config expects Optional[str]. We use "none" string in combo, convert to None?
        # Or let engine handle "none". Engine handles "none".

        return BarPlotConfig(
            **base_data,
            orientation=self.combo_orient.currentData(),
            estimator=self.combo_estimator.currentText(),
            errorbar=errorbar_val,
            capsize=self.spin_capsize.value(),
            width=self.spin_width.value(),
            alpha=self.spin_alpha.value(),
            linewidth=self.spin_linewidth.value(),
            edgecolor=self.combo_edgecolor.currentText() if self.combo_edgecolor.currentText() != "none" else None,
            palette=final_palette,
            overlays=StatisticalOverlayConfig() # Empty overlays for now, annotations supported via base methods if needed
        )
