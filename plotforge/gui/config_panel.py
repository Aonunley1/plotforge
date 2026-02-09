from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QGroupBox,
    QLineEdit,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QFrame,
    QScrollArea,
)
from PyQt5.QtCore import pyqtSignal, Qt, QSize

from plotforge.config import (
    ScatterPlotConfig,
    TrendlineConfig,
    SaveConfig,
    StatisticalOverlayConfig,
    AxesConfig,
    LegendConfig,
    KDEConfig,
    CIConfig,
    ReferenceLinesConfig,
    DEFAULT_PALETTE,
    DEFAULT_MARKERS,
)


# --- COLLAPSIBLE BOX HELPER ---
class CollapsibleBox(QWidget):
    def __init__(self, title="", parent=None, expanded=False):
        super().__init__(parent)

        self.toggle_button = QToolButton(text=title, checkable=True, checked=expanded)
        self.toggle_button.setStyleSheet(
            "QToolButton { border: none; font-weight: bold; }"
        )
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.toggle_button.toggled.connect(self.on_toggled)

        self.content_area = QWidget()
        self.content_area.setVisible(expanded)
        self.content_area.setStyleSheet(
            ".QWidget { border: 1px solid #dcdcdc; border-radius: 3px; }"
        )

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)

    def setLayout(self, layout):
        layout.setContentsMargins(10, 10, 10, 10)
        self.content_area.setLayout(layout)

    def on_toggled(self, checked):
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        self.content_area.setVisible(checked)


# ------------------------


class ConfigPanel(QWidget):
    update_signal = pyqtSignal()
    sheet_selected = pyqtSignal(str)  # New signal for sheet changes

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        # 1. Main Layout (Vertical)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- SHEET SELECTOR (New Feature) ---
        self.sheet_wrapper = QWidget()
        sheet_layout = QHBoxLayout(self.sheet_wrapper)
        sheet_layout.setContentsMargins(10, 10, 10, 5)

        self.lbl_sheet = QLabel("<b>Source Sheet:</b>")
        self.combo_sheet = QComboBox()
        self.combo_sheet.currentTextChanged.connect(self._on_sheet_change)

        sheet_layout.addWidget(self.lbl_sheet)
        sheet_layout.addWidget(self.combo_sheet, stretch=1)

        # Hidden by default, only shown for multi-sheet Excel files
        self.sheet_wrapper.setVisible(False)
        main_layout.addWidget(self.sheet_wrapper)
        # ------------------------------------

        # 2. Setup Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)  # Clean look

        # 3. Content Container for Scroll Area
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(10)

        # --- ADD SECTIONS TO SCROLL LAYOUT ---

        # A. Data Mapping
        data_group = CollapsibleBox("Data Mapping", expanded=True)
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
        data_group.setLayout(data_layout)
        self.scroll_layout.addWidget(data_group)

        # B. Scatter Settings
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
        self.combo_edgecolor.addItems(
            ["black", "white", "none", "gray", "red", "blue"]
        )

        self.combo_palette = QComboBox()
        self.combo_palette.addItem("Custom (Blue/Red/Green/Orange)", "custom")
        self.combo_palette.addItems(
            ["deep", "muted", "bright", "pastel", "dark", "colorblind"]
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
        self.scroll_layout.addWidget(scatter_group)

        # C. Visual Tweaks
        visual_group = CollapsibleBox(
            "Visual Tweaks (Axes, Ticks, Legend)", expanded=False
        )
        visual_layout = QFormLayout()

        self.line_xlabel = QLineEdit()
        self.line_xlabel.setPlaceholderText("Custom X Label (Optional)")
        self.line_ylabel = QLineEdit()
        self.line_ylabel.setPlaceholderText("Custom Y Label (Optional)")
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

        # Reference Lines (Updated: Two independent lines)
        visual_layout.addRow(QLabel("<b>Reference Lines</b>"))

        # Line 1 Row
        line1_layout = QHBoxLayout()
        self.check_line1 = QCheckBox("V-Line 1")
        self.check_line1.toggled.connect(self._toggle_ref_lines)
        self.spin_x1 = QDoubleSpinBox()
        self.spin_x1.setRange(-1e6, 1e6)
        self.spin_x1.setEnabled(False)
        self.spin_x1.setToolTip("X Position for Line 1")
        line1_layout.addWidget(self.check_line1)
        line1_layout.addWidget(self.spin_x1)
        visual_layout.addRow(line1_layout)

        # Line 2 Row
        line2_layout = QHBoxLayout()
        self.check_line2 = QCheckBox("V-Line 2")
        self.check_line2.toggled.connect(self._toggle_ref_lines)
        self.spin_x2 = QDoubleSpinBox()
        self.spin_x2.setRange(-1e6, 1e6)
        self.spin_x2.setEnabled(False)
        self.spin_x2.setToolTip("X Position for Line 2")
        line2_layout.addWidget(self.check_line2)
        line2_layout.addWidget(self.spin_x2)
        visual_layout.addRow(line2_layout)

        # Style Controls (Shared)
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
        self.spin_leg_x.setValue(0.5)
        self.spin_leg_x.setSingleStep(0.1)
        self.spin_leg_y = QDoubleSpinBox()
        self.spin_leg_y.setValue(1.1)
        self.spin_leg_y.setSingleStep(0.1)

        self.spin_leg_col = QSpinBox()
        self.spin_leg_col.setRange(0, 20)
        self.spin_leg_col.setValue(1)
        self.spin_leg_col.setSpecialValueText("Auto")

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
        self.line_legend_title.setPlaceholderText("Legend Title (Optional)")
        visual_layout.addRow("Legend Title:", self.line_legend_title)

        visual_group.setLayout(visual_layout)
        self.scroll_layout.addWidget(visual_group)

        # D. Statistical Overlays
        stats_group = CollapsibleBox("Statistical Overlays", expanded=False)
        stats_layout = QFormLayout()

        # -- Trendline --
        self.check_trendline = QCheckBox("Enable Trendline")
        self.check_trendline.toggled.connect(self._toggle_trendline_options)

        self.spin_order = QSpinBox()
        self.spin_order.setValue(1)
        self.spin_order.setEnabled(False)

        self.spin_trend_alpha = QDoubleSpinBox()
        self.spin_trend_alpha.setValue(1.0)
        self.spin_trend_alpha.setRange(0.0, 1.0)
        self.spin_trend_alpha.setSingleStep(0.1)
        self.spin_trend_alpha.setEnabled(False)

        self.spin_trend_width = QDoubleSpinBox()
        self.spin_trend_width.setValue(2.0)
        self.spin_trend_width.setEnabled(False)

        self.combo_trend_style = QComboBox()
        self.combo_trend_style.addItems(["-", "--", "-.", ":"])
        self.combo_trend_style.setEnabled(False)

        self.check_limit_range = QCheckBox("Limit Fit Range")
        self.check_limit_range.setEnabled(False)
        self.check_limit_range.toggled.connect(self._toggle_range_options)

        range_layout = QHBoxLayout()
        self.spin_fit_min = QDoubleSpinBox()
        self.spin_fit_min.setRange(-1e6, 1e6)
        self.spin_fit_min.setEnabled(False)
        self.spin_fit_max = QDoubleSpinBox()
        self.spin_fit_max.setRange(-1e6, 1e6)
        self.spin_fit_max.setValue(100.0)
        self.spin_fit_max.setEnabled(False)
        range_layout.addWidget(QLabel("Min:"))
        range_layout.addWidget(self.spin_fit_min)
        range_layout.addWidget(QLabel("Max:"))
        range_layout.addWidget(self.spin_fit_max)

        # -- Confidence Interval (Nested under Trendline) --
        ci_layout = QHBoxLayout()
        self.check_ci = QCheckBox("Show CI")
        self.check_ci.setEnabled(False)
        self.check_ci.toggled.connect(self._toggle_ci_options)

        self.spin_ci_level = QDoubleSpinBox()
        self.spin_ci_level.setRange(0.50, 0.999)
        self.spin_ci_level.setValue(0.95)
        self.spin_ci_level.setSingleStep(0.01)
        self.spin_ci_level.setEnabled(False)

        self.spin_ci_alpha = QDoubleSpinBox()
        self.spin_ci_alpha.setRange(0.0, 1.0)
        self.spin_ci_alpha.setValue(0.2)
        self.spin_ci_alpha.setSingleStep(0.1)
        self.spin_ci_alpha.setEnabled(False)

        ci_layout.addWidget(self.check_ci)
        ci_layout.addWidget(QLabel("Lvl:"))
        ci_layout.addWidget(self.spin_ci_level)
        ci_layout.addWidget(QLabel("Alpha:"))
        ci_layout.addWidget(self.spin_ci_alpha)

        stats_layout.addRow(self.check_trendline)
        stats_layout.addRow("Order:", self.spin_order)
        stats_layout.addRow("Alpha:", self.spin_trend_alpha)
        stats_layout.addRow("Width:", self.spin_trend_width)
        stats_layout.addRow("Style:", self.combo_trend_style)
        stats_layout.addRow(self.check_limit_range)
        stats_layout.addRow(range_layout)
        stats_layout.addRow(QLabel("Confidence Interval:"))
        stats_layout.addRow(ci_layout)

        # -- KDE --
        stats_layout.addRow(QLabel(""))
        stats_layout.addRow(QLabel("<b>KDE Density</b>"))
        self.check_kde = QCheckBox("Enable KDE")
        self.check_kde.toggled.connect(self._toggle_kde_options)

        self.check_kde_fill = QCheckBox("Fill")
        self.check_kde_fill.setChecked(True)
        self.check_kde_fill.setEnabled(False)

        self.combo_kde_cmap = QComboBox()
        self.combo_kde_cmap.addItems(
            [
                "mako",
                "rocket",
                "flare",
                "crest",
                "magma",
                "viridis",
                "icefire",
                "inferno",
            ]
        )
        self.combo_kde_cmap.setEnabled(False)

        self.spin_kde_alpha = QDoubleSpinBox()
        self.spin_kde_alpha.setRange(0.0, 1.0)
        self.spin_kde_alpha.setValue(0.5)
        self.spin_kde_alpha.setSingleStep(0.1)
        self.spin_kde_alpha.setEnabled(False)

        self.spin_kde_width = QDoubleSpinBox()
        self.spin_kde_width.setRange(0.0, 10.0)
        self.spin_kde_width.setValue(1.5)
        self.spin_kde_width.setSingleStep(0.5)
        self.spin_kde_width.setEnabled(False)

        stats_layout.addRow(self.check_kde)
        stats_layout.addRow("KDE Fill:", self.check_kde_fill)
        stats_layout.addRow("KDE Cmap:", self.combo_kde_cmap)
        stats_layout.addRow("KDE Alpha:", self.spin_kde_alpha)
        stats_layout.addRow("KDE Width:", self.spin_kde_width)

        stats_group.setLayout(stats_layout)
        self.scroll_layout.addWidget(stats_group)

        # E. Output Settings
        save_group = CollapsibleBox("Output Settings", expanded=False)
        save_layout = QFormLayout()
        self.spin_width = QDoubleSpinBox()
        self.spin_width.setValue(8.0)
        self.spin_height = QDoubleSpinBox()
        self.spin_height.setValue(6.0)
        self.spin_dpi = QSpinBox()
        self.spin_dpi.setRange(72, 600)
        self.spin_dpi.setValue(300)
        save_layout.addRow("W x H (in):", self.spin_width)
        save_layout.addRow("", self.spin_height)
        save_layout.addRow("DPI:", self.spin_dpi)
        save_group.setLayout(save_layout)
        self.scroll_layout.addWidget(save_group)

        # Add Stretch at end of scroll layout to push items up
        self.scroll_layout.addStretch()

        # 4. Finalize Main Layout
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # Update Button (Fixed at Bottom)
        self.btn_update = QPushButton("Update Plot")
        self.btn_update.clicked.connect(self.update_signal.emit)
        # Give it a bit of margin so it's not glued to the bottom edge
        button_container = QWidget()
        btn_layout = QVBoxLayout(button_container)
        btn_layout.setContentsMargins(10, 10, 10, 10)
        btn_layout.addWidget(self.btn_update)

        main_layout.addWidget(button_container)

    # --- Toggle Handlers ---
    def _toggle_limits(self, checked):
        self.spin_xmin.setEnabled(self.check_xlim.isChecked())
        self.spin_xmax.setEnabled(self.check_xlim.isChecked())
        self.spin_ymin.setEnabled(self.check_ylim.isChecked())
        self.spin_ymax.setEnabled(self.check_ylim.isChecked())

    def _toggle_ticks(self, checked):
        self.spin_x_major.setEnabled(checked)
        self.spin_y_major.setEnabled(checked)

    def _toggle_ref_lines(self):
        self.spin_x1.setEnabled(self.check_line1.isChecked())
        self.spin_x2.setEnabled(self.check_line2.isChecked())

    def _toggle_legend(self, checked):
        self.spin_leg_x.setEnabled(checked)
        self.spin_leg_y.setEnabled(checked)
        self.spin_leg_col.setEnabled(checked)

    def _toggle_trendline_options(self, checked):
        self.spin_order.setEnabled(checked)
        self.spin_trend_alpha.setEnabled(checked)
        self.spin_trend_width.setEnabled(checked)
        self.combo_trend_style.setEnabled(checked)
        self.check_limit_range.setEnabled(checked)
        self.check_ci.setEnabled(checked)

        if checked:
            if self.check_limit_range.isChecked():
                self._toggle_range_options(True)
            if self.check_ci.isChecked():
                self._toggle_ci_options(True)
        else:
            self._toggle_range_options(False)
            self._toggle_ci_options(False)

    def _toggle_range_options(self, checked):
        self.spin_fit_min.setEnabled(checked)
        self.spin_fit_max.setEnabled(checked)

    def _toggle_ci_options(self, checked):
        self.spin_ci_level.setEnabled(checked)
        self.spin_ci_alpha.setEnabled(checked)

    def _toggle_kde_options(self, checked):
        self.check_kde_fill.setEnabled(checked)
        self.combo_kde_cmap.setEnabled(checked)
        self.spin_kde_alpha.setEnabled(checked)
        self.spin_kde_width.setEnabled(checked)

    # --- Sheet Selection Handlers ---
    def _on_sheet_change(self, text):
        if text:
            self.sheet_selected.emit(text)

    def update_sheet_selector(self, sheets: list):
        """
        Populate the sheet dropdown. If multiple sheets exist, show the selector.
        """
        self.combo_sheet.blockSignals(True)
        self.combo_sheet.clear()

        if not sheets or len(sheets) <= 1:
            self.sheet_wrapper.setVisible(False)
        else:
            self.combo_sheet.addItems(sheets)
            self.sheet_wrapper.setVisible(True)

        self.combo_sheet.blockSignals(False)

    # --- Loading Columns (Unchanged) ---
    def load_columns(self, columns: list):
        self.combo_x.blockSignals(True)
        self.combo_y.blockSignals(True)
        self.combo_group.blockSignals(True)
        self.combo_style.blockSignals(True)
        self.combo_x.clear()
        self.combo_y.clear()
        self.combo_group.clear()
        self.combo_group.addItem("None", None)
        self.combo_style.clear()
        self.combo_style.addItem("None", None)
        self.combo_x.addItems(columns)
        self.combo_y.addItems(columns)
        self.combo_group.addItems(columns)
        self.combo_style.addItems(columns)
        self.combo_x.blockSignals(False)
        self.combo_y.blockSignals(False)
        self.combo_group.blockSignals(False)
        self.combo_style.blockSignals(False)

    # --- Build Config ---
    def build_config(self) -> "ScatterPlotConfig":
        # 1. Trendline
        fit_range = None
        if self.check_limit_range.isChecked():
            fit_range = (self.spin_fit_min.value(), self.spin_fit_max.value())

        trendline_config = TrendlineConfig(
            enabled=self.check_trendline.isChecked(),
            order=self.spin_order.value(),
            alpha=self.spin_trend_alpha.value(),
            linewidth=self.spin_trend_width.value(),
            linestyle=self.combo_trend_style.currentText(),
            fit_range=fit_range,
        )

        # 2. CI Config
        ci_config = CIConfig(
            enabled=self.check_ci.isChecked(),
            level=self.spin_ci_level.value(),
            alpha=self.spin_ci_alpha.value(),
        )

        # 3. KDE
        kde_config = KDEConfig(
            enabled=self.check_kde.isChecked(),
            fill=self.check_kde_fill.isChecked(),
            cmap=self.combo_kde_cmap.currentText(),
            alpha=self.spin_kde_alpha.value(),
            linewidth=self.spin_kde_width.value(),
        )

        # 4. Axes Visuals
        # Reference Lines
        ref_config = ReferenceLinesConfig(
            line1_enabled=self.check_line1.isChecked(),
            x1=self.spin_x1.value(),
            line2_enabled=self.check_line2.isChecked(),
            x2=self.spin_x2.value(),
            linewidth=self.spin_ref_width.value(),
            linestyle=self.combo_ref_style.currentText(),
            color="grey",
        )

        axes_config = AxesConfig(
            x_min=self.spin_xmin.value() if self.check_xlim.isChecked() else None,
            x_max=self.spin_xmax.value() if self.check_xlim.isChecked() else None,
            y_min=self.spin_ymin.value() if self.check_ylim.isChecked() else None,
            y_max=self.spin_ymax.value() if self.check_ylim.isChecked() else None,
            x_major_interval=(
                self.spin_x_major.value() if self.check_ticks.isChecked() else None
            ),
            y_major_interval=(
                self.spin_y_major.value() if self.check_ticks.isChecked() else None
            ),
            ref_lines=ref_config,
        )

        # 5. Legend
        bbox = None
        final_ncol = 1

        if self.check_legend_pos.isChecked():
            bbox = (self.spin_leg_x.value(), self.spin_leg_y.value())
            val = self.spin_leg_col.value()
            final_ncol = val if val > 0 else 1

        legend_config = LegendConfig(
            enabled=True,
            title=self.line_legend_title.text() or None,
            bbox_to_anchor=bbox,
            ncol=final_ncol,
        )

        # 6. Save
        save_config = SaveConfig(
            dpi=self.spin_dpi.value(),
            figure_size=(self.spin_width.value(), self.spin_height.value()),
        )

        # 7. Data/Style
        pal_data = self.combo_palette.currentData()
        final_palette = (
            DEFAULT_PALETTE
            if pal_data == "custom"
            else self.combo_palette.currentText()
        )

        marker_data = self.combo_markers.currentData()
        final_markers = DEFAULT_MARKERS if marker_data == "custom" else True

        group_col = (
            self.combo_group.currentText()
            if self.combo_group.currentIndex() != 0
            else None
        )
        style_col = (
            self.combo_style.currentText()
            if self.combo_style.currentIndex() != 0
            else None
        )

        config = ScatterPlotConfig(
            x=self.combo_x.currentText(),
            y=self.combo_y.currentText(),
            group_by=group_col,
            style_by=style_col,
            x_label=self.line_xlabel.text() or None,
            y_label=self.line_ylabel.text() or None,
            marker_size=self.spin_size.value(),
            alpha=self.spin_alpha.value(),
            linewidth=self.spin_linewidth.value(),
            edgecolor=self.combo_edgecolor.currentText(),
            palette=final_palette,
            markers=final_markers,
            overlays=StatisticalOverlayConfig(
                trendline=trendline_config, kde=kde_config, ci=ci_config
            ),
            axes=axes_config,
            legend=legend_config,
            save=save_config,
        )
        return config