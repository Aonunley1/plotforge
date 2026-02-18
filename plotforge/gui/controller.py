from PyQt5.QtCore import QObject
import pandas as pd

from plotforge.config import BasePlotConfig, ScatterPlotConfig, LinePlotConfig, HistogramConfig, BarPlotConfig, PlotResult
from plotforge.engine import ScatterPlotEngine, LinePlotEngine, HistogramPlotEngine, BarPlotEngine


class PlotController(QObject):
    """
    Ref: SPEC-2A Section 1
    """

    def execute(self, df: pd.DataFrame, config: 'BasePlotConfig') -> 'PlotResult':
        if isinstance(config, ScatterPlotConfig):
            engine = ScatterPlotEngine()
        elif isinstance(config, LinePlotConfig):
            engine = LinePlotEngine()
        elif isinstance(config, HistogramConfig):
            engine = HistogramPlotEngine()
        elif isinstance(config, BarPlotConfig):
            engine = BarPlotEngine()
        else:
            raise ValueError(f"Unsupported configuration type: {type(config)}")

        result = engine.execute(df, config)
        return result