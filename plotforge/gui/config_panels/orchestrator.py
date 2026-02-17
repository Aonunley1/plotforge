from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QStackedWidget,
    QLabel,
    QHBoxLayout,
    QFrame,
)
from PyQt5.QtCore import pyqtSignal

from plotforge.gui.config_panels.base_panel import BaseConfigPanel


class ConfigOrchestrator(QWidget):
    """
    Main container for the configuration sidebar.
    Manages switching between different plot-specific panels.
    """
    update_signal = pyqtSignal()
    sheet_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.panels: Dict[str, BaseConfigPanel] = {}
        self._init_ui()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Header with Plot Type Selector
        header_widget = QFrame()
        header_widget.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-bottom: 1px solid #dcdcdc;
            }
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #333;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 15, 10, 15)

        self.label_type = QLabel("Graph Type:")
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Scatter Plot", "Line Plot"])
        self.combo_type.currentTextChanged.connect(self._on_type_changed)

        header_layout.addWidget(self.label_type)
        header_layout.addWidget(self.combo_type, stretch=1)
        self.main_layout.addWidget(header_widget)

        # 2. Stacked Widget for Panels
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

    def register_panel(self, name: str, panel: BaseConfigPanel):
        """Register a new plot-specific panel and add it to the stack."""
        self.panels[name] = panel
        self.stacked_widget.addWidget(panel)
        
        # Connect internal signals to the Orchestrator's external signals
        panel.update_signal.connect(self.update_signal.emit)
        panel.sheet_selected.connect(self.sheet_selected.emit)

    def _on_type_changed(self, text: str):
        """Switch the visible panel when the dropdown changes."""
        if text in self.panels:
            self.stacked_widget.setCurrentWidget(self.panels[text])

    # --- Proxy Methods (Delegating to the active panel) ---
    def get_active_panel(self) -> BaseConfigPanel:
        return self.stacked_widget.currentWidget()

    def update_sheet_selector(self, sheets: List[str]):
        for panel in self.panels.values():
            panel.update_sheet_selector(sheets)

    def load_columns(self, columns: List[str]):
        for panel in self.panels.values():
            panel.load_columns(columns)

    def build_config(self) -> Any:
        """Calls build_config on the currently active panel."""
        active_panel = self.get_active_panel()
        if hasattr(active_panel, "build_config"):
            return active_panel.build_config()
        return None
