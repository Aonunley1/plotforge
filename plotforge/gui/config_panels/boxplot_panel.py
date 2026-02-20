from typing import Optional
from PyQt5.QtWidgets import (
    QFormLayout,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
)

from plotforge.config import BoxPlotConfig, StatisticalOverlayConfig, DEFAULT_PALETTE
from plotforge.gui.config_panels.base_panel import BaseConfigPanel, CollapsibleBox


class BoxPlotConfigPanel(BaseConfigPanel):
    """
    Configuration panel for Box Plots.
    Inherits shared UI from BaseConfigPanel.
    """
    def __init__(self, parent: Optional[BaseConfigPanel] = None):
        super().__init__(parent)
        self._relabel_axes()
        self._add_box_specific_ui()

    def _relabel_axes(self) -> None:
        """Rename the generic X/Y axis labels to category/value terminology."""
        layout = self.data_group.content_area.layout()
        x_label_widget = layout.labelForField(self.combo_x)
        if x_label_widget:
            x_label_widget.setText("Category (X):")
        y_label_widget = layout.labelForField(self.combo_y)
        if y_label_widget:
            y_label_widget.setText("Values (Y):")

    def _add_box_specific_ui(self):
        # Box Options
        box_group = CollapsibleBox("Box Options", expanded=True)
        box_layout = QFormLayout()

        # Orientation
        self.combo_orient = QComboBox()
        self.combo_orient.addItem("Vertical (y=Val)", "v")
        self.combo_orient.addItem("Horizontal (x=Val)", "h")
        
        # Features
        self.check_notch = QCheckBox("Notch (Median CI)")
        self.check_means = QCheckBox("Show Means")
        self.check_points = QCheckBox("Show Data Points (Stripplot)")
        
        # Visuals
        self.spin_box_width = QDoubleSpinBox()
        self.spin_box_width.setRange(0.1, 1.0)
        self.spin_box_width.setValue(0.8)
        self.spin_box_width.setSingleStep(0.1)
        
        self.spin_linewidth = QDoubleSpinBox()
        self.spin_linewidth.setRange(0.0, 5.0)
        self.spin_linewidth.setValue(1.5)
        
        self.spin_fliersize = QDoubleSpinBox()
        self.spin_fliersize.setRange(0.0, 20.0)
        self.spin_fliersize.setValue(5.0)
        
        self.combo_palette = self._build_palette_combo()

        box_layout.addRow("Orientation:", self.combo_orient)
        box_layout.addRow("Box Width:", self.spin_box_width)
        box_layout.addRow("Line Width:", self.spin_linewidth)
        box_layout.addRow("Outlier Size:", self.spin_fliersize)
        box_layout.addRow(self.check_notch)
        box_layout.addRow(self.check_means)
        box_layout.addRow(self.check_points)
        box_layout.addRow("Palette:", self.combo_palette)
        
        box_group.setLayout(box_layout)
        self.plot_options_container.addWidget(box_group)

    def build_config(self) -> BoxPlotConfig:
        base_data = self.build_base_config_data()
        
        palette_val = self.combo_palette.currentData()
        final_palette = DEFAULT_PALETTE if palette_val == "default" else self.combo_palette.currentText()
        
        return BoxPlotConfig(
            **base_data,
            orientation=self.combo_orient.currentData(),
            width=self.spin_box_width.value(),
            linewidth=self.spin_linewidth.value(),
            fliersize=self.spin_fliersize.value(),
            notch=self.check_notch.isChecked(),
            showmeans=self.check_means.isChecked(),
            show_data_points=self.check_points.isChecked(),
            palette=final_palette,
            overlays=StatisticalOverlayConfig() # Empty overlays by default
        )
