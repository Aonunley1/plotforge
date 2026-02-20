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
class ReferenceLinesConfig:
    # Line 1
    line1_enabled: bool = False
    x1: float = 0.0

    # Line 2
    line2_enabled: bool = False
    x2: float = 0

    # Shared Style
    linewidth: float = 1.5
    linestyle: str = "--"
    color: str = "grey"


@dataclass
class AxesConfig:
    # Limits (Bounds)
    x_min: Optional[float] = None
    x_max: Optional[float] = None
    y_min: Optional[float] = None
    y_max: Optional[float] = None

    # Tick Intervals — None means "let matplotlib decide"
    x_major_interval: Optional[float] = None
    y_major_interval: Optional[float] = None
    x_minor_interval: Optional[float] = None  # None = no minor ticks
    y_minor_interval: Optional[float] = None  # None = no minor ticks

    # Reference Lines (Replaces Range/VLine)
    ref_lines: ReferenceLinesConfig = field(default_factory=ReferenceLinesConfig)


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
    alpha: float = 0.5
    linewidth: float = 1.5


@dataclass
class CIConfig:
    enabled: bool = False
    level: float = 0.95
    alpha: float = 0.2


@dataclass
class ErrorBarConfig:
    """Configuration for error bars (works for scatter and line plots)"""
    enabled: bool = False
    
    # Error data column names (optional - can also use fixed values)
    y_error_column: Optional[str] = None  # Column name for Y errors
    x_error_column: Optional[str] = None  # Column name for X errors
    
    # Fixed error values (used if columns not specified)
    y_error: Optional[float] = None  # Fixed Y error value
    x_error: Optional[float] = None  # Fixed X error value
    
    # Styling
    linewidth: float = 1.5
    capsize: float = 3.0  # Cap size at the end of error bars
    capthick: float = 1.5  # Cap thickness
    alpha: float = 0.7
    color: Optional[str] = None  # None = use line/marker color


@dataclass
class LineCIConfig:
    """Configuration for confidence intervals around line plots.

    method maps directly to seaborn's errorbar parameter:
      "ci"  — bootstrap confidence interval (seaborn default, recommended)
      "se"  — standard-error band  (±1 SE by default)
      "sd"  — standard-deviation band
    """
    enabled: bool = False
    level: float = 0.95   # Used for "ci" (as a percentage: 95 → 95% CI)
    method: str = "ci"    # "ci" | "se" | "sd"

    # Styling — alpha for the shaded band
    alpha: float = 0.2


@dataclass
class AnnotationConfig:
    """Configuration for a single annotation"""
    # Position
    x: Optional[float] = None  # X coordinate
    y: Optional[float] = None  # Y coordinate
    
    # Text
    text: str = ""
    
    # Styling
    fontsize: float = 10.0
    color: str = "black"
    
    # Arrow (points from text to data point)
    arrow: bool = True
    arrow_style: str = "->"  # Options: "->", "-", "-[", "]-", etc.
    arrow_color: Optional[str] = None  # None = use text color
    
    # Text box
    bbox: bool = True
    bbox_facecolor: str = "white"
    bbox_edgecolor: str = "black"
    bbox_alpha: float = 0.8
    
    # Offset from point (in points)
    xytext_offset: Tuple[float, float] = (10, 10)


@dataclass
class AnnotationsConfig:
    """Configuration for multiple annotations"""
    enabled: bool = False
    
    # Manual annotations (list of AnnotationConfig)
    annotations: List[AnnotationConfig] = field(default_factory=list)
    
    # Automatic annotation modes
    annotate_peaks: bool = False  # Annotate local maxima
    annotate_troughs: bool = False  # Annotate local minima
    annotate_first: bool = False  # Annotate first point
    annotate_last: bool = False  # Annotate last point
    
    # Auto-annotation styling (used for automatic annotations)
    auto_fontsize: float = 9.0
    auto_color: str = "darkred"
    auto_arrow: bool = True
    auto_bbox: bool = True


@dataclass
class StatisticalOverlayConfig:
    trendline: TrendlineConfig = field(default_factory=TrendlineConfig)
    kde: KDEConfig = field(default_factory=KDEConfig)
    ci: CIConfig = field(default_factory=CIConfig)  # For trendline CI
    error_bars: ErrorBarConfig = field(default_factory=ErrorBarConfig)
    line_ci: LineCIConfig = field(default_factory=LineCIConfig)  # For line plot CI
    annotations: AnnotationsConfig = field(default_factory=AnnotationsConfig)  # Annotations





@dataclass
class BasePlotConfig:
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    group_by: Optional[str] = None
    style_by: Optional[str] = None

    # Shared color palette for all plot types
    palette: Union[List[str], str] = field(default_factory=lambda: DEFAULT_PALETTE.copy())

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
    # palette inherited from BasePlotConfig
    markers: Union[List[str], bool] = field(default_factory=lambda: DEFAULT_MARKERS.copy())
    # When set, x is divided into this many equal-width bins and the mean y per
    # bin is plotted instead of individual raw points.
    bins: Optional[int] = None


@dataclass
class LinePlotConfig(BasePlotConfig):
    """Configuration for line plots"""
    x: str = ""
    y: str = ""
    
    # Line styling
    linewidth: float = 2.5
    linestyle: str = "-"  # Options: "-", "--", "-.", ":"
    
    # Markers
    show_markers: bool = True
    marker_size: float = 8.0
    marker_style: str = "o"  # Options: "o", "s", "^", "v", "D", "X"
    
    # Fill options
    fill_between: bool = False
    fill_alpha: float = 0.3
    
    # Alpha for line
    alpha: float = 1.0
    
    # palette inherited from BasePlotConfig


@dataclass
class PlotResult:
    figure: Any
    artifacts: Dict[str, Any]
    warnings: List[str]


@dataclass
class HistogramConfig(BasePlotConfig):
    """Configuration for histogram plots"""
    x: str = ""
    # Note: Histogram doesn't typically use 'y' for input data unless horizontal.
    # BasePlotConfig doesn't enforce x/y fields.
    
    bins: Union[int, str] = "auto"
    stat: str = "count"  # count, frequency, probability, percent, density
    kde: bool = False
    cumulative: bool = False
    element: str = "bars" # bars, step, poly
    fill: bool = True
    log_scale: bool = False
    
    # Styling
    alpha: float = 0.5
    linewidth: float = 0.0
    edgecolor: Optional[str] = None
    
    # Palette inherited from BasePlotConfig


@dataclass
class BarPlotConfig(BasePlotConfig):
    """Configuration for bar plots"""
    x: str = ""
    y: str = ""
    
    # Orientation
    orientation: str = "v"  # 'v' for vertical, 'h' for horizontal
    
    # Aggregation
    estimator: str = "mean" # mean, median, sum, count, min, max
    errorbar: Optional[str] = "ci" # ci, pi, se, sd, None
    
    # Visuals
    width: float = 0.8  # Width of bars
    alpha: float = 0.8
    linewidth: float = 0.0
    edgecolor: Optional[str] = None
    
    # Capsize for error bars
    capsize: float = 0.1


@dataclass
class BoxPlotConfig(BasePlotConfig):
    """Configuration for box plots"""
    x: str = ""
    y: str = ""
    
    # Orientation
    orientation: str = "v"  # 'v' for vertical, 'h' for horizontal
    
    # Visuals
    width: float = 0.8
    linewidth: float = 1.5
    fliersize: float = 5.0  # Size of outlier markers
    
    # Features
    notch: bool = False
    showmeans: bool = False
    
    # Styling
    # Palette inherited, but boxprops/whiskerprops can be stylized if needed.
    # For now, base properties suffice.

