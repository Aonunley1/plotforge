# PlotForge

PlotForge is a modular, declarative Python application for generating complex, publication-ready statistical plots. It provides a PyQt5-based GUI to interactively design plots and a robust, abstracted backend engine powered by `seaborn` and `matplotlib` to execute them.

## Features

- **Multiple Plot Types**: Natively supports Line Plots, Scatter Plots, Bar Plots, Box Plots, and Histograms through an extensible engine architecture.
- **Advanced Statistical Overlays**: Automatically compute and chart confidence intervals (Bootstrap, SE, SD, PI), trendlines (linear, polynomial, exponential), KDEs, error bars, and distribution estimators on the fly.
- **Responsive & Dynamic UI**: Intuitive PyQT5 configuration panels to map data to categorical axes, semantic groups, and intricate style features.
- **Data-Driven Visuals**: Designed around `pandas` DataFrames. Intelligently parses datasets and automatically handles `NaN`s, edge cases, and dense structures.
- **Precise Image Exporting**: Decoupled rendering ensures that what you save is exactly what gets outputted to disk, irrespective of zoom level or display constraints. Supports precise dimension setting (e.g. strict 8x6 inches, 300 DPI) using exact `constrained_layout` handlers.
- **Extensive Testing Suite**: Backed by a comprehensive and growing pytest framework covering logic components, specific plot rendering behaviors, and auto-correcting dimensional output logic.

## Project Architecture

1.  **Plot Engines (`engine.py`)**: Abstract, object-oriented plot rendering systems. Subclasses encapsulate specific plot topologies (e.g. `LinePlotEngine`, `BoxPlotEngine`).
2.  **Configuration (`config.py`)**: Strong-typed dataclasses configuring everything from data-mapping down to individual grid styles.
3.  **UI Configuration Panels (`gui/config_panels/`)**: Highly organized UI segments handling plot-specific and base parameter setting before pushing to the config state.
4.  **Main App UI (`gui/main_window.py`)**: The primary interface for orchestrating the overall data loaded via standard tabular sources (Excel/CSV).

## Installation

PlotForge requires Python 3.10+ (tested against current stable releases). See `requirements.txt` for exact dependencies.

```bash
# Clone the repository
git clone [...]
cd plotforge

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Or `.venv\Scripts\activate` on Windows

# Install Dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
python run.py
```
*(Optionally you can run standard unit tests by executing `pytest tests/`)*
