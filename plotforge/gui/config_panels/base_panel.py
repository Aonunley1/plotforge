from typing import Optional, Tuple, List, Any
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QFrame,
    QScrollArea,
    QSpinBox,
)
from PyQt5.QtCore import pyqtSignal, Qt

from plotforge.config import (
    SaveConfig,
    AxesConfig,
    LegendConfig,
    ReferenceLinesConfig,
)


class CollapsibleBox(QWidget):
    """A premium-styled collapsible container for grouping UI controls."""
    def __init__(self, title: str = "", parent: Optional[QWidget] = None, expanded: bool = False):
        super().__init__(parent)

        self.toggle_button = QToolButton(text=title, checkable=True, checked=expanded)
        # Style controlled by MAIN_STYLESHEET
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.toggle_button.toggled.connect(self.on_toggled)

        self.content_area = QWidget()
        self.content_area.setObjectName("sectionContent")
        self.content_area.setVisible(expanded)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 5)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)

    def setLayout(self, layout: QVBoxLayout):
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        self.content_area.setLayout(layout)

    def on_toggled(self, checked: bool):
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        self.content_area.setVisible(checked)


class BaseConfigPanel(QWidget):
    """
    Base class for all plot configuration panels.
    Handles shared UI elements: Data Mapping, Axes, Legend, and Output Settings.
    """
    update_signal = pyqtSignal()
    sheet_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 1. Sheet Selector (Source Data)
        self.sheet_wrapper = QWidget()
        sheet_layout = QHBoxLayout(self.sheet_wrapper)
        sheet_layout.setContentsMargins(10, 10, 10, 5)

        self.lbl_sheet = QLabel("<b>Source Sheet:</b>")
        self.combo_sheet = QComboBox()
        self.combo_sheet.currentTextChanged.connect(self._on_sheet_change)

        sheet_layout.addWidget(self.lbl_sheet)
        sheet_layout.addWidget(self.combo_sheet, stretch=1)
        self.sheet_wrapper.setVisible(False)
        self.layout.addWidget(self.sheet_wrapper)

        # 2. Setup Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(12)  # Increased spacing for premium feel

        # --- SECTIONS ---
        
        # A. Data Mapping
        self.data_group = CollapsibleBox("Data Mapping", expanded=True)
        data_layout = QFormLayout()
        self.combo_x = QComboBox()
        self.combo_y = QComboBox()
        self.combo_group = QComboBox()
        self.combo_style = QComboBox()
        self.combo_group.addItem("None", None)
        self.combo_style.addItem("None", None)

        data_layout.addRow("X Axis:", self.combo_x)
        data_layout.addRow("Y Axis:", self.combo_y)
        data_layout.addRow("Group By:", self.combo_group)
        data_layout.addRow("Style By:", self.combo_style)
        self.data_group.setLayout(data_layout)
        self.scroll_layout.addWidget(self.data_group)

        # B. Plot Specific placeholder (to be inserted by subclasses)
        self.plot_options_container = QVBoxLayout()
        self.scroll_layout.addLayout(self.plot_options_container)

        # C. Visual Tweaks (Axes, Ticks, Legend)
        self.visual_group = CollapsibleBox("Visual Tweaks", expanded=False)
        visual_layout = QFormLayout()

        self.line_xlabel = QLineEdit()
        self.line_xlabel.setPlaceholderText("Custom X Label")
        self.line_ylabel = QLineEdit()
        self.line_ylabel.setPlaceholderText("Custom Y Label")
        visual_layout.addRow("Rename X:", self.line_xlabel)
        visual_layout.addRow("Rename Y:", self.line_ylabel)

        # Axes Limits
        lim_layout = QHBoxLayout()
        self.check_xlim = QCheckBox("Limit X")
        self.spin_xmin = QDoubleSpinBox()
        self.spin_xmin.setRange(-1e6, 1e6)
        self.spin_xmax = QDoubleSpinBox()
        self.spin_xmax.setRange(-1e6, 1e6)
        self.spin_xmax.setValue(100.0)
        self.check_xlim.toggled.connect(self._toggle_limits)
        lim_layout.addWidget(self.check_xlim)
        lim_layout.addWidget(QLabel("Min:"))
        lim_layout.addWidget(self.spin_xmin)
        lim_layout.addWidget(QLabel("Max:"))
        lim_layout.addWidget(self.spin_xmax)

        ylim_layout = QHBoxLayout()
        self.check_ylim = QCheckBox("Limit Y")
        self.spin_ymin = QDoubleSpinBox()
        self.spin_ymin.setRange(-1e6, 1e6)
        self.spin_ymax = QDoubleSpinBox()
        self.spin_ymax.setRange(-1e6, 1e6)
        self.spin_ymax.setValue(100.0)
        self.check_ylim.toggled.connect(self._toggle_limits)
        ylim_layout.addWidget(self.check_ylim)
        ylim_layout.addWidget(QLabel("Min:"))
        ylim_layout.addWidget(self.spin_ymin)
        ylim_layout.addWidget(QLabel("Max:"))
        ylim_layout.addWidget(self.spin_ymax)

        visual_layout.addRow(lim_layout)
        visual_layout.addRow(ylim_layout)

        # Tick Intervals
        tick_layout = QHBoxLayout()
        self.check_ticks = QCheckBox("Custom Ticks")
        self.spin_x_major = QDoubleSpinBox()
        self.spin_x_major.setValue(20.0)
        self.spin_y_major = QDoubleSpinBox()
        self.spin_y_major.setValue(2.0)
        self.check_ticks.toggled.connect(self._toggle_ticks)

        tick_layout.addWidget(self.check_ticks)
        tick_layout.addWidget(QLabel("X Major:"))
        tick_layout.addWidget(self.spin_x_major)
        tick_layout.addWidget(QLabel("Y Major:"))
        tick_layout.addWidget(self.spin_y_major)
        visual_layout.addRow(tick_layout)

        # Reference Lines
        visual_layout.addRow(QLabel("<b>Reference Lines (Vertical)</b>"))
        line1_layout = QHBoxLayout()
        self.check_line1 = QCheckBox("Line 1")
        self.check_line1.toggled.connect(self._toggle_ref_lines)
        self.spin_x1 = QDoubleSpinBox()
        self.spin_x1.setRange(-1e6, 1e6)
        self.spin_x1.setEnabled(False)
        line1_layout.addWidget(self.check_line1)
        line1_layout.addWidget(self.spin_x1)
        visual_layout.addRow(line1_layout)

        line2_layout = QHBoxLayout()
        self.check_line2 = QCheckBox("Line 2")
        self.check_line2.toggled.connect(self._toggle_ref_lines)
        self.spin_x2 = QDoubleSpinBox()
        self.spin_x2.setRange(-1e6, 1e6)
        self.spin_x2.setEnabled(False)
        line2_layout.addWidget(self.check_line2)
        line2_layout.addWidget(self.spin_x2)
        visual_layout.addRow(line2_layout)

        ref_style_layout = QHBoxLayout()
        self.spin_ref_width = QDoubleSpinBox()
        self.spin_ref_width.setRange(0.1, 10.0)
        self.spin_ref_width.setValue(1.5)
        self.combo_ref_style = QComboBox()
        self.combo_ref_style.addItems(["--", "-", "-.", ":"])
        ref_style_layout.addWidget(QLabel("Width:"))
        ref_style_layout.addWidget(self.spin_ref_width)
        ref_style_layout.addWidget(QLabel("Style:"))
        ref_style_layout.addWidget(self.combo_ref_style)
        ref_style_layout.addStretch()
        visual_layout.addRow(ref_style_layout)

        # Legend Position
        legend_layout = QHBoxLayout()
        self.check_legend_pos = QCheckBox("Custom Legend")
        self.spin_leg_x = QDoubleSpinBox()
        self.spin_leg_y = QDoubleSpinBox()
        self.spin_leg_col = QSpinBox()
        self.spin_leg_x.setValue(0.5)
        self.spin_leg_y.setValue(1.1)
        self.spin_leg_col.setValue(1)
        self.check_legend_pos.toggled.connect(self._toggle_legend)
        legend_layout.addWidget(self.check_legend_pos)
        legend_layout.addWidget(QLabel("X:"))
        legend_layout.addWidget(self.spin_leg_x)
        legend_layout.addWidget(QLabel("Y:"))
        legend_layout.addWidget(self.spin_leg_y)
        legend_layout.addWidget(QLabel("Cols:"))
        legend_layout.addWidget(self.spin_leg_col)
        visual_layout.addRow(legend_layout)

        self.line_legend_title = QLineEdit()
        self.line_legend_title.setPlaceholderText("Legend Title")
        visual_layout.addRow("Legend Title:", self.line_legend_title)

        self.visual_group.setLayout(visual_layout)
        self.scroll_layout.addWidget(self.visual_group)

        # D. Output Settings
        self.save_group = CollapsibleBox("Output Settings", expanded=False)
        save_layout = QFormLayout()
        self.spin_width = QDoubleSpinBox()
        self.spin_width.setValue(8.0)
        self.spin_height = QDoubleSpinBox()
        self.spin_height.setValue(6.0)
        self.spin_dpi = QSpinBox()
        self.spin_dpi.setRange(72, 600)
        self.spin_dpi.setValue(300)
        save_layout.addRow("Width (in):", self.spin_width)
        save_layout.addRow("Height (in):", self.spin_height)
        save_layout.addRow("DPI:", self.spin_dpi)
        self.save_group.setLayout(save_layout)
        self.scroll_layout.addWidget(self.save_group)

        # Finalize Scroll Area
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Update Button (Fixed at Bottom)
        self.btn_update = QPushButton("Update Plot")
        self.btn_update.clicked.connect(self.update_signal.emit)
        
        button_container = QWidget()
        btn_layout = QVBoxLayout(button_container)
        btn_layout.setContentsMargins(10, 10, 10, 10)
        btn_layout.addWidget(self.btn_update)
        self.layout.addWidget(button_container)

    # --- Handlers ---
    def _on_sheet_change(self, text: str):
        if text:
            self.sheet_selected.emit(text)

    def _toggle_limits(self):
        self.spin_xmin.setEnabled(self.check_xlim.isChecked())
        self.spin_xmax.setEnabled(self.check_xlim.isChecked())
        self.spin_ymin.setEnabled(self.check_ylim.isChecked())
        self.spin_ymax.setEnabled(self.check_ylim.isChecked())

    def _toggle_ticks(self, checked: bool):
        self.spin_x_major.setEnabled(checked)
        self.spin_y_major.setEnabled(checked)

    def _toggle_ref_lines(self):
        self.spin_x1.setEnabled(self.check_line1.isChecked())
        self.spin_x2.setEnabled(self.check_line2.isChecked())

    def _toggle_legend(self, checked: bool):
        self.spin_leg_x.setEnabled(checked)
        self.spin_leg_y.setEnabled(checked)
        self.spin_leg_col.setEnabled(checked)

    # --- Public API ---
    def update_sheet_selector(self, sheets: List[str]):
        self.combo_sheet.blockSignals(True)
        self.combo_sheet.clear()
        if not sheets or len(sheets) <= 1:
            self.sheet_wrapper.setVisible(False)
        else:
            self.combo_sheet.addItems(sheets)
            self.sheet_wrapper.setVisible(True)
        self.combo_sheet.blockSignals(False)

    def load_columns(self, columns: List[str]):
        widgets = [self.combo_x, self.combo_y, self.combo_group, self.combo_style]
        for w in widgets:
            w.blockSignals(True)
            w.clear()
            if w in [self.combo_group, self.combo_style]:
                w.addItem("None", None)
            w.addItems(columns)
            w.blockSignals(False)

    def build_base_config_data(self) -> dict:
        """Collects all base UI data into a dictionary for config construction."""
        
        # Legend
        bbox = None
        if self.check_legend_pos.isChecked():
            bbox = (self.spin_leg_x.value(), self.spin_leg_y.value())

        legend = LegendConfig(
            enabled=True,
            title=self.line_legend_title.text() or None,
            bbox_to_anchor=bbox,
            ncol=self.spin_leg_col.value() if self.spin_leg_col.value() > 0 else 1,
        )

        # Axes
        ref_lines = ReferenceLinesConfig(
            line1_enabled=self.check_line1.isChecked(),
            x1=self.spin_x1.value(),
            line2_enabled=self.check_line2.isChecked(),
            x2=self.spin_x2.value(),
            linewidth=self.spin_ref_width.value(),
            linestyle=self.combo_ref_style.currentText(),
        )

        axes = AxesConfig(
            x_min=self.spin_xmin.value() if self.check_xlim.isChecked() else None,
            x_max=self.spin_xmax.value() if self.check_xlim.isChecked() else None,
            y_min=self.spin_ymin.value() if self.check_ylim.isChecked() else None,
            y_max=self.spin_ymax.value() if self.check_ylim.isChecked() else None,
            x_major_interval=self.spin_x_major.value() if self.check_ticks.isChecked() else None,
            y_major_interval=self.spin_y_major.value() if self.check_ticks.isChecked() else None,
            ref_lines=ref_lines,
        )

        # Save
        save = SaveConfig(
            dpi=self.spin_dpi.value(),
            figure_size=(self.spin_width.value(), self.spin_height.value()),
        )

        return {
            "x": self.combo_x.currentText(),
            "y": self.combo_y.currentText(),
            "group_by": self.combo_group.currentText() if self.combo_group.currentIndex() != 0 else None,
            "style_by": self.combo_style.currentText() if self.combo_style.currentIndex() != 0 else None,
            "x_label": self.line_xlabel.text() or None,
            "y_label": self.line_ylabel.text() or None,
            "axes": axes,
            "legend": legend,
            "save": save,
        }
