from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvasQTAgg):
    """
    On-screen rendering always fills the available widget space.
    The figure's configured save size (figure_size / dpi) is only honoured
    when the user explicitly saves the file — not for the on-screen display.
    """

    def __init__(self, parent=None):
        fig = Figure()
        super().__init__(fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def set_figure(self, fig: Figure) -> None:
        old_fig = self.figure

        self.figure = fig
        self.figure.set_canvas(self)

        # Scale the figure to fill the current canvas widget dimensions.
        # This decouples the display size from config.save.figure_size so that
        # constrained_layout always has the full widget space to work with —
        # preventing "axes sizes collapsed to zero" on box plots with wide labels.
        dpi = fig.get_dpi()
        width_in = max(self.width(), 100) / dpi
        height_in = max(self.height(), 100) / dpi
        fig.set_size_inches(width_in, height_in, forward=False)

        self.draw()

        # Release artists from the old figure eagerly to avoid holding
        # matplotlib's internal render objects until GC runs.
        if old_fig is not None and old_fig is not fig:
            old_fig.clf()