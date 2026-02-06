import pandas as pd
from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex


class PandasModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None


class ArtifactTableView(QTableView):
    """
    Ref: SPEC-2A Section 1
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setAlternatingRowColors(True)

    def set_artifacts(self, artifacts: dict) -> None:
        self.setModel(None)
        if not artifacts: return

        target_df = None
        if "trendlines" in artifacts and isinstance(artifacts["trendlines"], pd.DataFrame):
            target_df = artifacts["trendlines"]
        else:
            for key, val in artifacts.items():
                if isinstance(val, pd.DataFrame):
                    target_df = val
                    break

        if target_df is not None:
            model = PandasModel(target_df)
            self.setModel(model)