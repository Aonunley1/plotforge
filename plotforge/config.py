from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Union

# --- DEFAULT STYLES ---
DEFAULT_RC_PARAMS = {
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': 'black',
    'axes.linewidth': 1.5,
    'xtick.direction': 'in', 'ytick.direction': 'in',
    'xtick.bottom': True, 'ytick.left': True,
    'xtick.major.size': 7, 'xtick.major.width': 1.5,
    'ytick.major.size': 7, 'ytick.major.width': 1.5,
    'xtick.minor.size': 5, 'xtick.minor.width': 1.5,
    'ytick.minor.size': 5, 'ytick.minor.width': 1.5,
    'lines.linewidth': 2.5,
    'axes.titlesize': 20, 'axes.labelsize': 20,
    'xtick.labelsize': 20, 'ytick.labelsize': 20,
    'legend.fontsize': 20, 'legend.title_fontsize': 20,
    'legend.frameon': True, 'legend.edgecolor': 'black',
    'legend.loc': 'upper left', 'legend.fancybox': True,
    'legend.labelspacing': .25, 'legend.handletextpad': 1,
    'legend.handlelength': .25, 'legend.columnspacing': 1,
    'legend.borderpad': 0.5,
    'figure.figsize': (8, 6),
    'savefig.dpi': 300,
    'figure.dpi': 100,
}

DEFAULT_PALETTE = ["blue", "red", "green", "orange"]
DEFAULT_MARKERS = ["o", "X", "^", "s"]


# --- CONFIG MODELS ---
@dataclass
class SaveConfig:
    dpi: int = 300
    figure_size: Tuple[float, float] = (8.0, 6.0)
    format: str = "png"


@dataclass
class AxesConfig:
    # Limits (Bounds)
    x_min: Optional[float] = None
    x_max: Optional[float] = None
    y_min: Optional[float] = None
    y_max: Optional[float] = None

    # Tick Intervals
    x_major_interval: Optional[float] = None
    y_major_interval: Optional[float] = None


@dataclass
class LegendConfig:
    enabled: bool = True
    title: Optional[str] = None
    bbox_to_anchor: Optional[Tuple[float, float]] = None
    ncol: Optional[int] = None
    location: str = "best"


@dataclass
class StyleConfig:
    theme: str = "white"
    font_scale: float = 1.0
    rc_params: Optional[Dict[str, Any]] = field(default_factory=lambda: DEFAULT_RC_PARAMS.copy())


@dataclass
class TrendlineConfig:
    enabled: bool = False
    order: int = 1
    fit_range: Optional[Tuple[float, float]] = None
    linewidth: float = 2.0
    linestyle: str = "-"
    alpha: float = 1.0


@dataclass
class KDEConfig:
    enabled: bool = False
    fill: bool = True
    cmap: str = "mako"
    bw_adjust: float = 1.0
    # --- NEW FIELDS ---
    alpha: float = 0.5
    linewidth: float = 1.5


@dataclass
class CIConfig:
    enabled: bool = False
    level: float = 0.95


@dataclass
class StatisticalOverlayConfig:
    trendline: Optional[TrendlineConfig] = None
    kde: Optional[KDEConfig] = None
    ci: Optional[CIConfig] = None


@dataclass
class BasePlotConfig:
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    group_by: Optional[str] = None
    style_by: Optional[str] = None

    style: StyleConfig = field(default_factory=StyleConfig)
    overlays: StatisticalOverlayConfig = field(default_factory=StatisticalOverlayConfig)
    legend: LegendConfig = field(default_factory=LegendConfig)
    axes: AxesConfig = field(default_factory=AxesConfig)
    save: SaveConfig = field(default_factory=SaveConfig)


@dataclass
class ScatterPlotConfig(BasePlotConfig):
    x: str = ""
    y: str = ""
    marker_size: float = 100.0
    alpha: float = 0.8
    linewidth: float = 1.0
    edgecolor: str = "black"
    palette: Union[List[str], str] = field(default_factory=lambda: DEFAULT_PALETTE.copy())
    markers: Union[List[str], bool] = field(default_factory=lambda: DEFAULT_MARKERS.copy())


@dataclass
class PlotResult:
    figure: Any
    artifacts: Dict[str, Any]
    warnings: List[str]