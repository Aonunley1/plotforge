from typing import Optional
from PyQt5.QtWidgets import (
    QFormLayout,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QLabel,
    QHBoxLayout,
)

from plotforge.config import (
    LinePlotConfig,
    LineCIConfig,
    StatisticalOverlayConfig,
    DEFAULT_PALETTE,
)
from plotforge.gui.config_panels.base_panel import BaseConfigPanel, CollapsibleBox


class LineConfigPanel(BaseConfigPanel):
    """
    Configuration panel for Line Plots.
    Inherits shared UI from BaseConfigPanel and adds line-specific options.
    """
    def __init__(self, parent: Optional[BaseConfigPanel] = None):
        super().__init__(parent)
        self._add_line_specific_ui()

    def _add_line_specific_ui(self):
        # 1. Line Style Options
        line_group = CollapsibleBox("Line Options", expanded=True)
        line_layout = QFormLayout()

        self.spin_linewidth = QDoubleSpinBox()
        self.spin_linewidth.setRange(0.5, 10.0)
        self.spin_linewidth.setValue(2.5)
        self.spin_linewidth.setSingleStep(0.5)

        self.combo_linestyle = QComboBox()
        self.combo_linestyle.addItems(["-", "--", "-.", ":"])

        self.spin_alpha = QDoubleSpinBox()
        self.spin_alpha.setRange(0.0, 1.0)
        self.spin_alpha.setValue(1.0)
        self.spin_alpha.setSingleStep(0.1)

        line_layout.addRow("Line Width:", self.spin_linewidth)
        line_layout.addRow("Line Style:", self.combo_linestyle)
        line_layout.addRow("Opacity:", self.spin_alpha)

        # 2. Marker Options (within Line Plot)
        marker_layout = QHBoxLayout()
        self.check_markers = QCheckBox("Show Markers")
        self.check_markers.setChecked(True)
        self.check_markers.toggled.connect(self._toggle_marker_options)

        self.combo_marker_style = QComboBox()
        self.combo_marker_style.addItems(["o", "s", "^", "v", "D", "X"])
        
        self.spin_marker_size = QDoubleSpinBox()
        self.spin_marker_size.setRange(1.0, 20.0)
        self.spin_marker_size.setValue(8.0)

        marker_layout.addWidget(self.check_markers)
        marker_layout.addWidget(QLabel("Style:"))
        marker_layout.addWidget(self.combo_marker_style)
        marker_layout.addWidget(QLabel("Size:"))
        marker_layout.addWidget(self.spin_marker_size)
        line_layout.addRow("Markers:", marker_layout)

        # 3. Fill Options
        fill_layout = QHBoxLayout()
        self.check_fill = QCheckBox("Fill Below")
        self.check_fill.toggled.connect(self._toggle_fill_options)
        self.spin_fill_alpha = QDoubleSpinBox()
        self.spin_fill_alpha.setRange(0.0, 1.0)
        self.spin_fill_alpha.setValue(0.3)
        self.spin_fill_alpha.setEnabled(False)
        
        fill_layout.addWidget(self.check_fill)
        fill_layout.addWidget(QLabel("Fill Alpha:"))
        fill_layout.addWidget(self.spin_fill_alpha)
        line_layout.addRow("Area Fill:", fill_layout)

        line_group.setLayout(line_layout)

        # 4. Statistical Overlays (Line Specific)
        stats_group = CollapsibleBox("Statistical Overlays", expanded=False)
        stats_layout = QFormLayout()

        # Confidence Interval (Line CI)
        ci_layout = QHBoxLayout()
        self.check_line_ci = QCheckBox("Show CI (Shared Data)")
        self.check_line_ci.toggled.connect(self._toggle_ci_options)
        
        self.combo_ci_method = QComboBox()
        self.combo_ci_method.addItems(["ci", "se", "sd"])
        self.combo_ci_method.setToolTip(
            "ci = Bootstrap CI (recommended)\n"
            "se = ±1 Standard Error band\n"
            "sd = ±1 Standard Deviation band"
        )
        self.combo_ci_method.setEnabled(False)

        self.spin_ci_level = QDoubleSpinBox()
        self.spin_ci_level.setRange(0.50, 0.99)
        self.spin_ci_level.setValue(0.95)
        self.spin_ci_level.setEnabled(False)

        ci_layout.addWidget(self.check_line_ci)
        ci_layout.addWidget(QLabel("Method:"))
        ci_layout.addWidget(self.combo_ci_method)
        ci_layout.addWidget(QLabel("Lvl:"))
        ci_layout.addWidget(self.spin_ci_level)
        stats_layout.addRow(ci_layout)

        stats_group.setLayout(stats_layout)

        # Add to the reserved placeholder in BaseConfigPanel
        self.plot_options_container.addWidget(line_group)
        self.plot_options_container.addWidget(stats_group)

    def _toggle_marker_options(self, checked: bool):
        self.combo_marker_style.setEnabled(checked)
        self.spin_marker_size.setEnabled(checked)

    def _toggle_fill_options(self, checked: bool):
        self.spin_fill_alpha.setEnabled(checked)

    def _toggle_ci_options(self, checked: bool):
        self.combo_ci_method.setEnabled(checked)
        self.spin_ci_level.setEnabled(checked)

    def build_config(self) -> LinePlotConfig:
        base_data = self.build_base_config_data()

        # Line CI
        line_ci = LineCIConfig(
            enabled=self.check_line_ci.isChecked(),
            method=self.combo_ci_method.currentText(),
            level=self.spin_ci_level.value(),
        )

        return LinePlotConfig(
            **base_data,
            linewidth=self.spin_linewidth.value(),
            linestyle=self.combo_linestyle.currentText(),
            alpha=self.spin_alpha.value(),
            show_markers=self.check_markers.isChecked(),
            marker_size=self.spin_marker_size.value(),
            marker_style=self.combo_marker_style.currentText(),
            fill_between=self.check_fill.isChecked(),
            fill_alpha=self.spin_fill_alpha.value(),
            overlays=StatisticalOverlayConfig(line_ci=line_ci),
            palette=DEFAULT_PALETTE,
        )
