import pandas as pd
from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant

# Mapping raw engine keys to User-Friendly Headers
COLUMN_MAP = {
    "group": "Group",
    "n": "N",
    "r2": "R²",
    "p_value": "P-Value",
    "slope": "Slope",
    "intercept": "Intercept",
    "slope_lower": "Slope (Low)",
    "slope_upper": "Slope (High)",
    "intercept_lower": "Int. (Low)",
    "intercept_upper": "Int. (High)",
    "slope_std_err": "Slope SE",
    "intercept_std_err": "Int. SE",
    "order": "Order"
}

# Educational Tooltips for headers
TOOLTIP_MAP = {
    "r2": "Coefficient of Determination (0 to 1).\nIndicates how well the trendline fits the data.\n1.0 is a perfect fit.",
    "p_value": "Probability of observing these results by chance.\n• P < 0.05: Statistically Significant\n• P > 0.05: Not Significant (Result might be random noise)",
    "slope": "The rate of change (Y per unit X).\nHow steep the line is.",
    "intercept": "The value of Y when X is 0.",
    "slope_std_err": "Standard Error of the Slope.\n• Low SE: High precision (reliable estimate)\n• High SE: Low precision (noisy data)",
    "intercept_std_err": "Standard Error of the Intercept.\nMeasure of uncertainty in the starting point.",
    "slope_lower": "95% Confidence Interval (Lower Bound).\nIf the Interval (Low to High) crosses 0, the relationship is NOT statistically significant.",
    "slope_upper": "95% Confidence Interval (Upper Bound).\nIf the Interval (Low to High) crosses 0, the relationship is NOT statistically significant.",
    "intercept_lower": "95% Confidence Interval for Intercept.\nIf this range crosses 0, the intercept is statistically indistinguishable from zero.",
    "intercept_upper": "95% Confidence Interval for Intercept.\nIf this range crosses 0, the intercept is statistically indistinguishable from zero.",
    "n": "Sample Size (Number of data points used for this fit)."
}

# Define the preferred order of columns
# Order: Group -> N -> Stats -> Estimates -> CIs -> SEs
COLUMN_ORDER = [
    "group",
    "n",
    "r2",
    "p_value",
    "slope",
    "intercept",
    "slope_lower",
    "slope_upper",
    "intercept_lower",
    "intercept_upper",
    "slope_std_err",
    "intercept_std_err"
]


class PandasModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._data.shape[0]

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._data.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            val = self._data.iloc[index.row(), index.column()]

            # Formatting floats to be readable (4 sig figs)
            if isinstance(val, (float, int)):
                # Check for integer-like floats to avoid "100.0000"
                if isinstance(val, float) and val.is_integer():
                    return str(int(val))
                return "{:.4g}".format(val)

            return str(val)

        elif role == Qt.TextAlignmentRole:
            # Right-align numbers, Left-align text
            val = self._data.iloc[index.row(), index.column()]
            if isinstance(val, (int, float)):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> QVariant:
        col_name = str(self._data.columns[section])

        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                # Use the mapped name if available, otherwise use original column name
                return COLUMN_MAP.get(col_name, col_name)

            elif role == Qt.ToolTipRole:
                # Return the educational tooltip if available
                return TOOLTIP_MAP.get(col_name, None)

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
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
        # Clear the current model
        self.setModel(None)

        if not artifacts: return

        target_df = None

        # Prioritize the 'trendlines' dataframe if it exists
        if "trendlines" in artifacts and isinstance(artifacts["trendlines"], pd.DataFrame):
            raw_df = artifacts["trendlines"]

            if raw_df.empty:
                return

            # 1. Filter and Reorder Columns
            # Only include columns that actually exist in the dataframe
            # This handles cases where some stats might be missing (e.g. higher order polynomials)
            existing_cols = [col for col in COLUMN_ORDER if col in raw_df.columns]

            # If we found matches, create a filtered view.
            if existing_cols:
                target_df = raw_df[existing_cols].copy()
            else:
                # Fallback: just show everything if our expected columns aren't there
                target_df = raw_df.copy()

        # Fallback for other artifact types (KDE, etc.) if needed in future
        else:
            for key, val in artifacts.items():
                if isinstance(val, pd.DataFrame):
                    target_df = val
                    break

        if target_df is not None:
            model = PandasModel(target_df)
            self.setModel(model)