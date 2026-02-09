from typing import List, Optional
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QDialogButtonBox,
)


class SheetSelectionDialog(QDialog):
    """
    A modal dialog that forces the user to select a specific sheet
    from an Excel file before processing can continue.
    """

    def __init__(self, sheet_names: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Excel Sheet")
        self.setFixedWidth(300)

        # State to store the result
        self.selected_sheet: Optional[str] = None

        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Instruction Label
        self.label = QLabel("This file contains multiple sheets.\nPlease select one:")
        self.layout.addWidget(self.label)

        # Dropdown for Sheet Names
        self.sheet_combo = QComboBox()
        self.sheet_combo.addItems(sheet_names)
        self.layout.addWidget(self.sheet_combo)

        # Dialog Buttons (OK / Cancel)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept_selection)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def accept_selection(self) -> None:
        """
        Captures the currently selected text before closing the dialog.
        """
        self.selected_sheet = self.sheet_combo.currentText()
        self.accept()