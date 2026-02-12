# PlotForge

A configuration-driven desktop application for creating publication-quality scientific plots with Python.

---

## 🎯 Overview

PlotForge is a PyQt5-based GUI application that enables researchers and data scientists to create high-quality plots through an intuitive interface. It emphasizes configurability, reproducibility, and publication-ready output.

### Key Features

- **Multiple Plot Types**
  - Scatter plots with statistical overlays
  - Line plots with markers and fill options
  - *(More plot types coming soon: bar, box, violin, heatmap)*

- **Statistical Overlays**
  - Polynomial trendlines (any order)
  - Confidence intervals
  - Kernel density estimation (KDE)

- **Advanced Styling**
  - Custom color palettes
  - Grouped data visualization
  - Style-based markers
  - Configurable axes, legends, and labels

- **Publication-Ready Output**
  - High-resolution export (300+ DPI)
  - Multiple format support (PNG, SVG, PDF)
  - Precise control over figure dimensions

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/Aonunley1/plotforge.git
cd plotforge

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

- **GUI**: PyQt5
- **Data**: pandas, numpy
- **Plotting**: matplotlib, seaborn
- **Statistics**: statsmodels

---

## 🚀 Quick Start

### GUI Application

```bash
python -m plotforge.main
```

1. Load data (CSV or Excel)
2. Select plot type
3. Configure plot settings
4. Click "Update Plot"
5. Export to file

### Programmatic Usage

```python
import pandas as pd
from plotforge.config import LinePlotConfig
from plotforge.engine import LinePlotEngine

# Load your data
df = pd.read_csv('data.csv')

# Configure plot
config = LinePlotConfig(
    x='time',
    y='temperature',
    group_by='sensor',
    title='Temperature Over Time',
    x_label='Time (hours)',
    y_label='Temperature (°C)',
    linewidth=2.5,
    show_markers=True
)

# Generate plot
engine = LinePlotEngine()
result = engine.execute(df, config)

# Save
result.figure.savefig('output.png', dpi=300, bbox_inches='tight')
```

---

## 📊 Supported Plot Types

### Scatter Plot
- Grouped data with color mapping
- Style-based markers
- Polynomial trendlines
- Confidence intervals
- KDE overlays

### Line Plot
- Single or multiple lines
- Markers (toggle, size, style)
- Line styles (solid, dashed, dotted, dash-dot)
- Fill between line and x-axis
- Custom color palettes

### Coming Soon
- Bar plots
- Box plots
- Violin plots
- Heatmaps

---

## 🏗️ Project Structure

```
plotforge/
├── plotforge/              # Source code
│   ├── config.py          # Configuration dataclasses
│   ├── engine.py          # Plot engines (template method pattern)
│   ├── main.py            # Application entry point
│   └── gui/               # GUI components (MVC-like)
│       ├── main_window.py
│       ├── controller.py
│       ├── config_panel.py
│       ├── plot_canvas.py
│       └── artifact_table.py
│
├── tests/                  # Test suite
│   ├── test_lineplot.py
│   ├── test_optimizations.py
│   └── README.md          # Testing documentation
│
└── README.md              # This file
```

---

## 🧪 Testing

### Run Tests

```bash
# Basic line plot test
python tests/test_lineplot.py

# Comprehensive test suite
python tests/test_lineplot_comprehensive.py

# Unit tests
pytest tests/test_optimizations.py
```

### Test Coverage

- ✅ Color mapping and palettes
- ✅ Statistical overlays (trendlines, KDE, CI)
- ✅ Error handling (NaN values, insufficient data)
- ✅ Performance optimizations (caching)
- ✅ Line plot features (markers, styles, fill)

See `tests/README.md` for detailed testing documentation.

---

## 🛠️ Development

### Architecture

PlotForge uses a **template method pattern** for plot engines:

- **`BasePlotEngine`**: Defines the plotting workflow
  - Shared helper methods (color mapping, validation)
  - Configurable overlays and styling
  
- **Concrete Engines**: Implement plot-specific logic
  - `ScatterPlotEngine`
  - `LinePlotEngine`
  - *(More coming soon)*

### Adding a New Plot Type

1. Create config class in `config.py`:
   ```python
   @dataclass
   class MyPlotConfig(BasePlotConfig):
       # Plot-specific fields
       pass
   ```

2. Create engine in `engine.py`:
   ```python
   class MyPlotEngine(BasePlotEngine):
       def draw_core(self, ax, df, config):
           # Plot-specific implementation
           pass
   ```

3. Update `PlotController` in `gui/controller.py`

4. Add GUI controls in `gui/config_panel.py`

### Code Style

- **Type hints**: Required for all function signatures
- **Formatting**: Black style, 100 character line length
- **Imports**: Grouped (stdlib, third-party, local)
- **Docstrings**: For public functions and classes

---

## 📝 Configuration

PlotForge uses dataclasses for configuration:

```python
@dataclass
class LinePlotConfig(BasePlotConfig):
    x: str                      # X column name
    y: str                      # Y column name
    linewidth: float = 2.5      # Line width
    show_markers: bool = True   # Show markers
    fill_between: bool = False  # Fill area under line
    # ... inherits palette, title, labels, etc.
```

All plot types inherit from `BasePlotConfig`:
- Title, labels, grouping
- Color palettes
- Style configuration
- Axes configuration
- Legend configuration
- Statistical overlays
- Save options

---

## 🎨 Examples

### Scatter Plot with Trendline

```python
from plotforge.config import ScatterPlotConfig, TrendlineConfig
from plotforge.engine import ScatterPlotEngine

config = ScatterPlotConfig(
    x='x_data',
    y='y_data',
    group_by='category',
    title='Scatter Plot with Trendline',
    overlays=StatisticalOverlayConfig(
        trendline=TrendlineConfig(
            enabled=True,
            order=1,  # Linear
            linewidth=2.0
        )
    )
)

engine = ScatterPlotEngine()
result = engine.execute(df, config)
result.figure.savefig('scatter.png', dpi=300)
```

### Line Plot with Custom Palette

```python
from plotforge.config import LinePlotConfig

config = LinePlotConfig(
    x='time',
    y='value',
    group_by='sensor',
    title='Multi-Sensor Data',
    palette=['#FF6B6B', '#4ECDC4', '#45B7D1'],  # Custom colors
    show_markers=True,
    marker_style='o',
    fill_between=True,
    fill_alpha=0.2
)

engine = LinePlotEngine()
result = engine.execute(df, config)
result.figure.savefig('lines.png', dpi=300)
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make your changes**
4. **Run tests**: `pytest tests/`
5. **Commit with clear messages**: `git commit -m "Add feature X"`
6. **Push to your fork**: `git push origin feature/my-feature`
7. **Open a Pull Request**

### Development Workflow

- Use the `feature/` branch naming convention
- Write tests for new features
- Update documentation as needed
- Follow existing code style

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🗺️ Roadmap

### Current Version (v0.1)
- ✅ Scatter plots
- ✅ Line plots
- ✅ Statistical overlays (trendlines, KDE, CI)
- ✅ GUI application

### Planned Features
- ⏳ Bar plots
- ⏳ Box plots
- ⏳ Violin plots
- ⏳ Heatmaps
- ⏳ Plot templates
- ⏳ Batch processing
- ⏳ Export to multiple formats
- ⏳ Interactive plot editing

---

## 📧 Contact

- **Repository**: https://github.com/Aonunley1/plotforge
- **Issues**: https://github.com/Aonunley1/plotforge/issues

---

## 🙏 Acknowledgments

Built with:
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Matplotlib](https://matplotlib.org/) - Plotting library
- [Seaborn](https://seaborn.pydata.org/) - Statistical visualization
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Statsmodels](https://www.statsmodels.org/) - Statistical modeling

---

**Version**: 0.1.0  
**Last Updated**: 2026-02-12
